# Markitdown

**What it does:** Converts a file — PDF, Word document, PowerPoint, Excel spreadsheet, image, audio file, webpage, and more — into clean Markdown text that's easy to read or edit. It also offers to clean up common conversion glitches (broken sentences, missing headings) before finalizing anything, and always asks before overwriting a file.

This skill is a wrapper around Microsoft's open-source [`markitdown`](https://github.com/microsoft/markitdown) conversion tool — all credit for the actual file conversion goes to that project. This skill just adds the automatic install and the before/after cleanup review on top of it.

**Requirements:** The first time you use it, it installs a small free tool it depends on automatically — provided one baseline tool is already on your machine (true for almost everyone, but see the fallback below if not):

- **macOS** — needs [Homebrew](https://brew.sh). If missing, the skill will tell you and link you to install it, or you can run `pip install "markitdown[all]"` yourself.
- **Linux** (including WSL) — needs `pip`, `pip3`, or `pipx` (standard on virtually every Linux install). If none are found, install Python's pip (e.g. `sudo apt install python3-pip` on Debian/Ubuntu) and try again.
- **Windows** — needs Python already installed. If missing, install it from [python.org](https://python.org) (tick "Add python.exe to PATH" during setup) and try again.

**Try it by asking Claude something like:**
> "Convert this PDF to Markdown for me" (attach or point to the file)

Claude will find the file, convert it, and show you a before/after of any cleanup it suggests — nothing gets overwritten without your OK.

**Running this in claude.ai (no Claude Code needed):** unlike Claude Code, browser chat doesn't keep an installed skill "switched on" in the background — you attach the skill's files to the specific request instead:
1. Attach the skill's `SKILL.md` and `scripts/ensure_markitdown.sh` files, along with the file you want converted, to your message.
2. Ask something like: "Using the attached skill and script, convert this PDF."
