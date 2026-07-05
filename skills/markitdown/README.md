# Markitdown

## What it does

Converts a file — PDF, Word document, PowerPoint, Excel spreadsheet, image, audio file, webpage, and more — into clean Markdown text that's easy to read or edit. It also offers to clean up common conversion glitches (broken sentences, missing headings) before finalizing anything, and always asks before overwriting a file.

This skill is a wrapper around Microsoft's open-source [`markitdown`](https://github.com/microsoft/markitdown) conversion tool — all credit for the actual file conversion goes to that project. This skill just adds the automatic install and the before/after cleanup review on top of it.

## Prerequisites

The first time you use it, it installs a small free tool it depends on automatically — provided one baseline tool is already on your machine (true for almost everyone, but see the fallback below if not):

- **macOS** — needs [Homebrew](https://brew.sh). If missing, the skill will tell you and link you to install it, or you can run `pip install "markitdown[all]"` yourself.
- **Linux** (including WSL) — needs `pip`, `pip3`, or `pipx` (standard on virtually every Linux install). If none are found, install Python's pip (e.g. `sudo apt install python3-pip` on Debian/Ubuntu) and try again.
- **Windows** — needs Python already installed. If missing, install it from [python.org](https://python.org) (tick "Add python.exe to PATH" during setup) and try again.

## Usage

**Try it by asking Claude something like:**
> "Convert this PDF to Markdown for me" (attach or point to the file)

Claude will find the file, convert it, and show you a before/after of any cleanup it suggests — nothing gets overwritten without your OK.

**Running this in claude.ai (no Claude Code needed):** unlike Claude Code, browser chat doesn't keep an installed skill "switched on" in the background — you attach the skill's files to the specific request instead:
1. Attach the skill's `SKILL.md` and `scripts/ensure_markitdown.sh` files, along with the file you want converted, to your message.
2. Ask something like: "Using the attached skill and script, convert this PDF."

## Sample output

**Prompt:**
> "Convert the attached PDF to markdown for me"

**Response:**
> Converting the PDF now using the markitdown skill.
>
> No existing `.md` file to worry about. Now installing markitdown if needed and running the conversion.
>
> Conversion succeeded. Now reviewing the output for artifacts before proposing any cleanup.
>
> The conversion succeeded, but the source was a two-column table (topic → guidance) that came out completely flattened into two disconnected blocks of text, plus a ligature glitch where "ti" renders as "7" throughout (e.g. "sec7on" → "section", "7tle" → "title"). Per the skill, I won't touch the file until you approve the cleanup — here's what I'm proposing to reconstruct:
>
> **Ligature/encoding fixes (mechanical, throughout):** "7" → "ti" (section, citions, optional, etc.), "ﬁ" → "fi" (figures, first, etc.), stray tabs between words → single spaces.
>
> **Structural fix:** The topics (Page size, Font, Citations, Title, Abstract, etc.) and their guidance text got separated into two blocks during extraction. I've matched them back into a proper table by content, e.g.:
>
> | Topic | Guidance |
> |---|---|
> | Page size | A4 |
> | Page layout | Include a running header with your name and ecs user id (e.g. Frederica Savonarola, fs918g). Include a running footer with title of the report and the current page number |
> | Margins | Margins of 1 inch (2.54cm) on every side is reasonable |
> | Font | Use Sans Serif fonts, no smaller than 10 point. I suggest 11 or 12 point for body text and 10 point for references |
> | ... | ... |
>
> Section headings ("Overall content", "Front matter", "Body text", "Optional sections", "General advice") get promoted to `##` headers. Page-footer numbers ("1", "2") are dropped as artifacts.
>
> Given the scale of reassembly here (roughly 25 topic/guidance pairs to re-pair correctly), I'd rather you sanity-check my full reconstruction before I write it, instead of just a diff snippet.
>
> Want me to:
> 1. Write the fully reconstructed file now for you to review in place, or
> 2. Show the complete proposed markdown text here in chat first?

**Follow-up:**
> "Write the fully reconstructed file now"

**Response:**
> Confirmed the exact wording. Writing the fully reconstructed file now.
>
> The file is written to `Research Report Style Guide.md`.
>
> What changed: reconstructed the flattened two-column table (topic → guidance) that markitdown pulled apart into two disconnected blocks, promoted section labels to headings, fixed the font's broken ligature encoding throughout (e.g. "sec7on"→"section", "ma7er"→"matter", "lecer"→"letter", "hcp://"→"http://"), and corrected "GPDR" to "GDPR" (a typo, likely from the original document rather than the conversion).
>
> What needs your attention: the "Title content (figures & tables)" and "Table titles" rows were out of sequence in the raw extraction relative to the topic list at the top of the source — I matched them to their guidance text by content/context rather than position, since the original table structure isn't recoverable exactly. Worth a quick skim against the original PDF layout if precision here matters to you.

## Troubleshooting

**"Homebrew is required but not installed" (macOS).**
See [Prerequisites](#prerequisites) above — install Homebrew (or run `pip install "markitdown[all]"` yourself instead), then ask Claude to try the conversion again.
