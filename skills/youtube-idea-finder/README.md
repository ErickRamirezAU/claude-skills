# YouTube Idea Finder

**What it does:** Searches YouTube for a topic and finds videos where the view count is unusually high compared to how many subscribers the channel has — a sign of a small creator who unexpectedly went viral. Useful for content research, finding collaborators, or scouting a niche.

The idea for this skill was inspired by [Shane Hummus](https://www.youtube.com/@ShaneHummus)'s YouTube videos on channel strategy and finding proven video ideas — this skill automates that "find videos overperforming their channel size" research.

**Compatibility:** this skill only works in **Claude Code**. It needs real outbound network access to call the YouTube Data API, which isn't available in claude.ai's browser chat or in Cowork — both run in a sandboxed environment that only allows a fixed list of domains (github, pypi, npm, etc.), and the YouTube API isn't on that list.

**Before your first use — get a free API key:**
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

**Try it by asking Claude something like:**
> "Find me small YouTube channels that blew up talking about home coffee roasting."

Claude will tell you what search settings it's using (minimum views, max subscribers, etc.) before running the search, and hand back a table of results with links.
