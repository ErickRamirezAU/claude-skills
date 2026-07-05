# YouTube Idea Finder

## What it does

Searches YouTube for a topic and finds videos where the view count is unusually high compared to how many subscribers the channel has — a sign of a small creator who unexpectedly went viral. Useful for content research, finding collaborators, or scouting a niche.

The idea for this skill was inspired by [Shane Hummus](https://www.youtube.com/@ShaneHummus)'s YouTube videos on channel strategy and finding proven video ideas — this skill automates that "find videos overperforming their channel size" research.

> [!WARNING]
> This skill only works in **Claude Code**. It needs real outbound network access to call the YouTube Data API, which isn't available in claude.ai's browser chat or in Cowork — both run in a sandboxed environment that only allows a fixed list of domains (github, pypi, npm, etc.), and the YouTube API isn't on that list.

## Before your first use — get a free API key

This skill needs a YouTube Data API key from Google. It's free and doesn't require a credit card.

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project (or use an existing one).
3. Enable the **YouTube Data API v3**.
4. Go to **APIs & Services → Credentials → Create Credentials → API key** and copy the key it gives you.

Then save it so Claude can find it:

- **macOS:** Open the **Terminal** app, and run:
  ```
  echo 'export YOUTUBE_API_KEY="paste-your-key-here"' >> ~/.zshenv
  ```
  Then close and reopen Terminal (or the app running Claude).

- **Windows:** Open **PowerShell**, and run:
  ```
  setx YOUTUBE_API_KEY "paste-your-key-here"
  ```
  Close and reopen the terminal/app for it to take effect.

## Usage

**Try it by asking Claude something like:**
> "Find me small YouTube channels that blew up talking about home coffee roasting."

Claude will tell you what search settings it's using (minimum views, max subscribers, etc.) before running the search, and hand back a table of results with links.

## Sample output

**Prompt:**
> "Find me small YouTube channels which had high performing videos talking about RAG application tutorial"

**Response:**

Found 5 videos on "RAG application tutorial" that are overperforming their channel size (thresholds: min 100K views, max 100K subscribers, min 5:1 view-to-subscriber ratio):

| Title | Views | Subscribers | Channel | Ratio | Link |
|---|---|---|---|---|---|
| LangChain Explained in 13 Minutes \| QuickStart Tutorial for Beginners | 1,119,601 | 36,000 | Rabbitmetrics | 31.1:1 | [link](https://www.youtube.com/watch?v=aywZrzNaKjs) |
| RAG vs MCP: Which One Makes AI Smarter? | 102,331 | 3,480 | CodeCraft Academy | 29.41:1 | [link](https://www.youtube.com/watch?v=7D1nUK9ONEY) |
| Python RAG Tutorial (with Local LLMs): AI For Your PDFs | 628,606 | 83,700 | pixegami | 7.51:1 | [link](https://www.youtube.com/watch?v=2TJxpyO3ei4) |
| You Can Learn AI Agent System Design In 19 Min \| RAG, Vector Database, Evals, Function Calling | 102,142 | 18,100 | Sean's AI Stories | 5.64:1 | [link](https://www.youtube.com/watch?v=CyLYY_xb5bQ) |
| RAG + Langchain Python Project: Easy AI/Chat For Your Docs | 471,339 | 83,700 | pixegami | 5.63:1 | [link](https://www.youtube.com/watch?v=tcqEUSNCn8I) |

Hit the target count on the first search pass — no need to widen the search. Quota used: ~510 units out of the default 10,000/day.
