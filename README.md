# claude-skills

A small collection of **Skills** for [Claude](https://claude.ai) — Anthropic's AI assistant.

If you've never heard of Skills before: think of them as an instruction booklet you hand to Claude that teaches it how to do one specific job really well, step by step, using the right tools along the way. Without the booklet, Claude has to guess at the details each time. With it, Claude follows the exact process someone already figured out and tested.

No coding knowledge is required to use any of them — you just need Claude installed, and you'll copy a folder into place (or upload it, if you're using the app). Full steps below.

---

## What are Skills, exactly?

A Skill is a bundle of written instructions (plus, sometimes, a small helper script) that teaches Claude a specific, repeatable task — the same way a new employee gets a runbook for a task they'll do often, instead of figuring it out from scratch every time. Claude reads the instructions when the task comes up and follows them, including things like which tools to use, what questions to ask you, and how to format the results.

You don't need to understand how they work under the hood to use them — just install one (see below) and ask Claude to do the thing it's designed for, in plain English.

**Further reading:** for Anthropic's own explanation of Skills, see their documentation at [docs.claude.com](https://docs.claude.com) (search "Agent Skills" if the page has moved — Anthropic reorganizes its docs from time to time).

---

## Table of contents

- [What are Skills, exactly?](#what-are-skills-exactly)
- [What you need first](#what-you-need-first)
- [Step 1: Download the skills](#step-1-download-the-skills)
- [Step 2: Install a skill](#step-2-install-a-skill)
  - [Option A — Claude Desktop or claude.ai (no terminal needed)](#option-a--claude-desktop-or-claudeai-no-terminal-needed)
  - [Option B — Claude Code (command line / IDE)](#option-b--claude-code-command-line--ide)
- [Using the skills](#using-the-skills)
- [Updating to a newer version](#updating-to-a-newer-version)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## What you need first

You need **one** of the following (not both):

- **Claude Desktop app or claude.ai in your browser**, with a Claude account — this is the easiest route and works the same on Mac and Windows, or
- **Claude Code** (the terminal/developer tool) installed on your computer — this route involves copying a folder into a hidden system folder, which is slightly more technical but only takes a minute.

If you're not sure which one you use, and you just chat with Claude in a browser tab or a desktop app window, you're using [option A](#option-a--claude-desktop-or-claudeai-no-terminal-needed).

---

## Step 1: Download the skills

You don't need to know Git or the command line for this part.

1. Go to this repository's page on GitHub.
2. Click the green **`< > Code`** button near the top.
3. Click **Download ZIP**.
4. Find the downloaded file (usually in your **Downloads** folder) and double-click it to unzip it.
   - **Mac**: double-clicking unzips it automatically into a folder called `claude-skills-main`.
   - **Windows**: right-click the ZIP file and choose **Extract All...**, then choose a location and click **Extract**.

Inside, you'll find a `skills` folder containing one folder per skill (e.g. `youtube-idea-finder`, `markitdown`, and any others that have been added since). Each of those folders is the whole skill — you'll use the entire folder, not a single file inside it.

*(If you're comfortable with Git, you can instead run `git clone` on this repository's URL — same result, faster to update later.)*

---

## Step 2: Install a skill

### Option A — Claude Desktop or claude.ai (no terminal needed)

1. Open Claude (desktop app or claude.ai in your browser) and sign in.
2. Go to **Settings**.
3. Look for a section called **Capabilities** or **Skills** (the exact wording may shift slightly as Claude updates, but it will be under Settings).
4. Choose **Upload a skill** (or similar) and select the skill folder you unzipped in Step 1 — e.g. `youtube-idea-finder` or `markitdown`.
   - If the uploader asks for a `.zip` file specifically rather than a folder, right-click the skill's folder and choose **Compress** (Mac) or **Send to → Compressed (zipped) folder** (Windows), then upload that instead.
5. Repeat for each additional skill you want to use.

That's it — the skill is now available whenever you chat with Claude.

### Option B — Claude Code (command line / IDE)

Claude Code looks for skills in a specific folder on your computer. Copy each skill folder there:

- **macOS or Linux:**
  ```
  ~/.claude/skills/
  ```
  In Finder, press `Cmd+Shift+G`, type `~/.claude/skills`, and drag in whichever skill folder(s) you want (e.g. `youtube-idea-finder`, `markitdown`). If the `skills` folder doesn't exist yet, create it.

- **Windows (running Claude Code natively):**
  ```
  %USERPROFILE%\.claude\skills\
  ```
  Open File Explorer, paste that path into the address bar, and press Enter. Copy the skill folder(s) in. If the folder doesn't exist, create it.

- **Windows using WSL (Windows Subsystem for Linux):**
  Use the macOS/Linux path above (`~/.claude/skills/`) *inside* your WSL terminal, since Claude Code is running in the Linux environment.

Restart Claude Code (or start a new session) after copying the files so it notices the new skill.

---

## Using the skills

This repository contains a growing collection of skills. Currently available:

| Skill | What it does |
|---|---|
| [`youtube-idea-finder`](skills/youtube-idea-finder/README.md) | Finds YouTube videos that "overperformed" — huge view counts from small, under-the-radar channels — for any topic you give it. Great for content research and finding hidden gems. |
| [`markitdown`](skills/markitdown/README.md) | Converts files (PDFs, Word docs, PowerPoints, Excel sheets, images, audio, and more) into clean, readable, editable Markdown text. |

More skills will be added over time — check back, or watch this repository on GitHub to be notified.

You don't need to "run" a skill directly — just ask Claude to do the task in plain English once it's installed. See each skill's own README (linked above) for what it does, its requirements, compatibility notes, and example prompts.

---

## Updating to a newer version

If this repository gets updated later:

- **If you downloaded the ZIP:** repeat [Step 1](#step-1-download-the-skills) to get a fresh copy, then repeat [Step 2](#step-2-install-a-skill) to replace the old folder with the new one.
- **If you used `git clone`:** run `git pull` inside the `claude-skills` folder, then copy the updated skill folder(s) into place again.

---

## Troubleshooting

**Claude doesn't seem to use the skill even though I installed it.**
Make sure you copied/uploaded the *entire* skill folder (including its `scripts` subfolder), not just the `SKILL.md` file on its own — the skill needs both. Also try starting a new conversation, since skills are picked up at the start of a session.

**"Homebrew is required but not installed" (Markitdown, Mac).**
Install Homebrew from [brew.sh](https://brew.sh), then ask Claude to try the conversion again.

**The YouTube skill says the API key is missing or invalid.**
Double check you saved the key with the exact commands in the [YouTube Idea Finder README](skills/youtube-idea-finder/README.md), and that you opened a *new* terminal window/app session afterward — the key won't be picked up by windows that were already open.

**I'm not sure which install option (A or B) applies to me.**
If you talk to Claude through a website or a desktop app window with a normal chat interface, use Option A. If you type commands into a terminal to talk to Claude, use Option B.

---

## Contributing

Contributions are welcome — whether that's fixing a typo, improving a skill's instructions, or adding a brand new skill.

- **Found a bug or have an idea?** Open an [issue](../../issues) describing what's wrong or what you'd like to see.
- **Want to submit a change yourself?** See [instructions for contributing](CONTRIBUTING.md).

You don't need to be a programmer to contribute — improving the plain-English wording in a `SKILL.md` file or in this README is just as valuable as a code change.

If you'd like to discuss contributions, do a collab or just chat, you can get in touch with me at the coordinates listed on my website [8567.me](https://8567.me).

---

## License

MIT — see [LICENSE](LICENSE). Use, copy, and modify freely.
