---
name: markitdown
description: >
  Converts files (PDF, DOCX, PPTX, XLSX, images, audio, HTML, CSV/JSON/XML,
  ZIP, YouTube URLs) to clean Markdown using Microsoft's markitdown CLI, and
  optionally reviews the result for extraction artifacts (fragmented
  sentences, missing headings, ligature glitches, spelling errors). Use this
  skill whenever the user attaches a file and asks to convert it, extract
  text/content from it, "turn this into markdown," get a readable or
  editable version of a PDF or Office doc, or mentions markitdown by name —
  even if they just say something like "can you get the text out of this" or
  "make this PDF editable."
---

# markitdown

Convert a source file to Markdown, save it next to the source, and — only
with explicit approval — clean up formatting artifacts left over from the
conversion.

This skill wraps [markitdown](https://github.com/microsoft/markitdown),
Microsoft's open-source CLI for converting files to Markdown — all credit
for the actual conversion goes to that project. This skill only adds the
install-and-fix-up workflow around it.

## Step 1: Resolve the input

The input may arrive as an attached file, a bare filename, or a full path.

- If it's a full path or attachment, use it directly.
- If it's a bare filename, check the current directory first, then common
  locations like `~/Downloads` and `~/Desktop`. If you find more than one
  match or none, ask the user rather than guessing — picking the wrong file
  is worse than asking a quick question.

## Step 2: Make sure markitdown is installed

Run `scripts/ensure_markitdown.sh`. It checks whether `markitdown` is on
PATH, already installed at `~/.local/bin/markitdown`, or importable as a
Python module even without a console-script entrypoint (covers venvs,
system package managers, and non-standard pip installs) — and only installs
it if none of those find it. No need to ask before installing. This mirrors
how it was set up the first time, so re-running it on a machine that
already has markitdown is a fast no-op.

The install path is platform-aware:
- **macOS** uses Homebrew (`python@3.12`, `pipx`), the reliable standard there.
- **Linux** (including WSL, which reports as Linux) prefers `pipx`/`pip3`/`pip`
  directly and never requires Homebrew, since most Linux users won't have it.
- **Native Windows** (Git Bash/MSYS/Cygwin, not WSL) looks for `python3`,
  `python`, or the `py` launcher, uses `pipx` if present or `pip install
  --user` otherwise, and checks `%APPDATA%\Python\PythonXY\Scripts` for the
  installed executable — pip's Windows install location, which isn't
  `~/.local/bin`.

If the script still fails after that, surface the error to the user rather
than trying alternate install methods — the failure usually means something
about the machine needs their attention first (e.g. no pip available at
all).

**Important:** each shell command you run is typically a fresh process, so
a `PATH` fix made by the script doesn't carry over to the next command.
Source the script (`source scripts/ensure_markitdown.sh`) in the *same*
shell invocation as the actual conversion in Step 3, rather than running it
as a standalone step — that way the corrected `PATH` is still in effect
when `markitdown` is invoked.

## Step 3: Convert

The output path is always the source file's directory + the source's base
filename + `.md` — i.e., convert it in place, next to the original. This
keeps converted files discoverable and colocated with what they came from,
the same way `document.pdf` and `document.md` sit side by side.

Before writing, check whether that `.md` path already exists. If it does,
**ask the user** whether to overwrite it, save under a different name, or
skip the conversion — don't guess, since an existing `.md` file next to the
source might be someone's prior edits, not just a stale artifact.

Run the conversion:
```bash
markitdown "<source path>" -o "<output path>"
```

If the command fails, report the error plainly and stop — don't attempt the
review step on a conversion that didn't succeed.

## Step 4: Review pass (only after a successful conversion)

Markitdown's extraction is mechanical, so certain artifacts show up
predictably, especially from PDFs and Office documents:

- **Fragmented sentences** — lines broken mid-sentence or mid-list-item
  because the source PDF wrapped text at a fixed width. Rejoin these into
  proper paragraphs and list items.
- **Missing headings** — a document's title and section names often come
  through as plain paragraphs. Look for text that's clearly acting as a
  title or section label (short, standalone, followed by body text) and
  promote it to the appropriate `#`/`##`/`###` level.
- **Ligature and encoding glitches** — things like `ﬁ` instead of `fi`, or
  mismatched smart quotes.
- **Flattened tables** — a table in the source sometimes comes out as loose
  runs of text with no visual structure. Reconstruct it as a proper Markdown
  table or list if the row/column structure is still recoverable from
  context.
- **Likely typos** — obvious spelling mistakes that look like they came from
  OCR or extraction noise rather than the author's intent.

Read the converted file yourself and identify which of these apply. Then
show the user a clear before/after (a diff, or a summary of the specific
changes) **in the chat** — do not touch the file yet. The point is to let
them see exactly what's changing before it's permanent, since automated
cleanup can occasionally "fix" something that was actually correct in the
original.

## Step 5: Apply only on approval

If the user approves, write the cleaned-up version to the `.md` file. If
they want adjustments, iterate on the proposal first. If they decline or
don't respond affirmatively, leave the raw conversion output untouched —
the unedited markitdown output is still a valid, usable result on its own.
