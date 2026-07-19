# YouTube Video Evaluator

## What it does

Takes a batch of YouTube video candidates — usually the output of the [`youtube-idea-finder`](../youtube-idea-finder/README.md) skill — and produces an actionable diagnostic report per video: what its thumbnail and editing actually look like and why, what topics/tech/format it covers, and a concrete "replicate this, fix that, do this for your own calendar" brief.

This skill doesn't search YouTube or apply any pass/fail filter itself — every candidate handed to it gets a full write-up, whether its packaging is great or terrible. The point isn't to find gaps to exploit, it's to reverse-engineer what worked (and what didn't) well enough to turn it into a content calendar entry.

It only consumes `youtube-idea-finder`'s output (or a manually supplied list of video IDs/URLs) — it never modifies that skill.

## Limitations

> [!WARNING]
> Like `youtube-idea-finder`, this skill only works in **Claude Code**, since it needs real outbound network access to call the YouTube Data API and to fetch storyboard images (not available in claude.ai's browser chat or in Cowork).

## Prerequisites

- Uses the same `YOUTUBE_API_KEY` as `youtube-idea-finder` — see that skill's [Prerequisites](../youtube-idea-finder/README.md#prerequisites) section for how to get and save one. No separate key is needed.
- `yt-dlp` and `ffmpeg` on your `PATH`, used to pull the static scrub-bar preview frames it judges editing quality from (no video playback involved):
  - **macOS:** `brew install yt-dlp` — `ffmpeg` is usually already present; if not, `brew install ffmpeg`.
  - **Linux:** `pipx install yt-dlp` (or `pip install yt-dlp`) and `sudo apt install ffmpeg` (Debian/Ubuntu) or your distro's equivalent.
  - **Windows:** install both via [winget](https://learn.microsoft.com/windows/package-manager/winget/) (`winget install yt-dlp.yt-dlp` and `winget install ffmpeg`) or follow each project's own install instructions.

## Usage

**Try it by asking Claude something like:**

1. Right after a `youtube-idea-finder` run:
   > "Evaluate the candidates from that last search."
2. With your own list of videos, no finder run needed:
   > "Evaluate these YouTube videos: [url1], [url2], [url3]"
3. Both in one request — Claude runs the finder first, then feeds its results straight into the evaluator:
   > 'Run the video idea evaluator on "no-code AI tools".'

Claude fetches metadata and thumbnails for each video, samples three storyboard frames (0s/45s/90s) to judge editing quality, pulls out topics/tech/format, and hands back a single downloadable Markdown file (`Video Ideas - [search terms].md`) with a summary table up top and a full breakdown per video underneath.

## Sample output

**Prompt:**
> 'Run the video idea evaluator on "vibecode with Claude".'

**Response:**
> Found 4 videos on "vibecode with Claude" overperforming their channel size (max 5 pages searched, hit `max_pages_reached` before reaching 5 candidates). Fetching metadata, thumbnails, and storyboard frames for each now.
>
> | # | Title | Channel | Ratio | Format |
> |---|---|---|---|---|
> | 1 | [Học Claude Code từ con số 0 → Build AI Projects, Sub-Agents & Automation từ A–Z trong 2 giờ](https://www.youtube.com/watch?v=g-ZtK5u-iiw) | Thanh Trần - 5 Phút AI | 15.61:1 | Full-course talking-head walkthrough |
> | 2 | [How I use Claude Code (Meta Staff Engineer Tips)](https://www.youtube.com/watch?v=mZzhfPle9QU) | John Kim | 14.27:1 | Numbered pro-tips list |
> | 3 | [Vibe coding beautiful UIs in 3 simple steps](https://www.youtube.com/watch?v=p_q7-iW606U) | Morning Maker Show with Sandra and Dan | 13.81:1 | Hands-on build (3-step) |
> | 4 | [How To Use Claude Code In Vscode - Learn AI In 5 Minutes Series](https://www.youtube.com/watch?v=Nmr02XA9n1o) | Jonathan Acuña - Doctor AI | 6.3:1 | Quick-tutorial explainer |
>
> ---
>
> ## 2. How I use Claude Code (Meta Staff Engineer Tips)
>
> | Field | Detail |
> |---|---|
> | Channel | John Kim |
> | Link | https://www.youtube.com/watch?v=mZzhfPle9QU |
> | Views / Subscribers / Ratio | 456,724 / 32,000 / 14.27:1 |
> | Format | Numbered pro-tips list, 46:12 |
> | Topics | CLAUDE.md structure, keyboard shortcuts, slash commands, hooks, sub-agents, git worktrees, MCP, parallel Claude instances |
> | Tech/tools | Claude Code, CLAUDE.md, MCP, git worktrees, iTerm |
> | Thumbnail | **Good.** Bold pixel-art "CLAUDE CODE" text, high-contrast orange-on-black, expressive raised-hand gesture matching the "Pro Tips" hook, clear single payoff. |
> | Editing | **Good.** 0s/45s hold on a talking-head cold open; by 90s it cuts to an on-screen numbered tip card ("1. Run from root.") over a terminal screen-share with a framed PiP webcam — real structural progression matching the "50 tips" premise. |
>
> **What to replicate:**
> - Numbered-tip framing ("50 tips from N months of daily use") gives the video structure and skimmability
> - Pixel-art bold thumbnail text pairs one expressive gesture with a single hook word
> - On-screen numbered tip cards over the screen-share reinforce the list structure while watching
>
> **What to fix:**
> - The cold open holds on a static talking-head for at least 45 seconds before the first on-screen tip card appears — pulling the first numbered tip forward would hook viewers faster
>
> **Calendar action:** A numbered "N tips from M months of X" video, pixel-art bold-text thumbnail with one gesture plus a hook word, on-screen numbered cards over the screen-share.
>
> ---
>
> ## 1. Học Claude Code từ con số 0 → Build AI Projects, Sub-Agents & Automation từ A–Z trong 2 giờ
>
> | Field | Detail |
> |---|---|
> | Channel | Thanh Trần - 5 Phút AI |
> | Link | https://www.youtube.com/watch?v=g-ZtK5u-iiw |
> | Views / Subscribers / Ratio | 344,993 / 22,100 / 15.61:1 |
> | Format | Full-course talking-head walkthrough, 2h11m |
> | Topics | Claude Code setup, CLAUDE.md, hooks, slash commands, MCP, sub-agents/agent teams, git worktrees, context management, cloud deploy |
> | Tech/tools | Claude Code, Antigravity IDE, MCP, Modal |
> | Thumbnail | **Good.** Bold two-tone "CLAUDE CODE TỪ A ĐẾN Z" text, thinking-pose face, two framed code-editor screenshots as background collage, neon blue/pink "1 CLIP LÀM CHỦ LUÔN" hook banner. |
> | Editing | **Bad.** Checkpoints at 0s/45s/90s all show near-identical static talking-head framing in a well-lit studio (RGB accents, monitor, plants) — no cuts or screen-share visible yet despite covering a full multi-topic course. |
>
> **What to replicate:**
> - The topic itself — a complete, from-zero course scoped to one whole tool — proves demand at scale regardless of pacing
> - Studio production value (lighting, monitor, decor) signals credibility even before any screen-share appears
>
> **What to fix:**
> - No cuts or screen-share visible in the first 90 seconds of a 2+ hour course — bring the first live demo forward much sooner to prove the "hands-on" promise early
>
> **Calendar action:** A from-zero full-course video on one tool, but cut to the first live screen-share demo inside the first 30-45 seconds instead of holding on talking-head.
>
> ---
>
> Entries 3 and 4 follow the same structure (one more Good/Good, one Mediocre thumbnail/Good editing) and are in the full report.

## Troubleshooting

**Claude says the API key is missing or invalid.**
Same fix as `youtube-idea-finder` — see [its Troubleshooting section](../youtube-idea-finder/README.md#troubleshooting).

**Claude says `yt-dlp` or `ffmpeg` isn't found.**
Install whichever is missing per [Prerequisites](#prerequisites) above, then ask Claude to try again — no other setup needed.

**Claude says a video has no storyboard formats.**
Rare, but some videos don't have YouTube-generated scrub-bar previews. Claude will mark editing quality as unassessed for that one video rather than guess — everything else in its report is unaffected.
