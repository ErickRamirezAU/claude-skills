---
name: youtube-idea-finder
description: Finds YouTube videos that are "overperforming" for their channel size — high view counts from small/under-the-radar channels — for a given topic or search term. Use this whenever the user wants to find hidden-gem, underrated, or viral-outlier YouTube videos in a niche; wants examples of small creators who "went viral" or beat the algorithm on a specific topic; is scouting a niche for content strategy, competitor research, or collaboration ideas; or asks to search YouTube and filter results by view count, subscriber count, or a views-to-subscribers ratio. Trigger even if the user doesn't use the words "ratio" or "subscribers" explicitly — phrases like "find me small channels that blew up talking about X" or "what videos are punching above their weight for [topic]" describe the same task.
---

# YouTube Idea Finder

Idea and name credit: inspired by [Shane Hummus](https://www.youtube.com/@ShaneHummus)'s
YouTube videos on channel strategy and finding proven video ideas — this skill
automates that "find videos overperforming their channel size" research.

Find videos on a given topic where the view count is large relative to the
channel's subscriber count — a signal that a small or unknown creator produced
something that broke out beyond their usual audience. This uses the YouTube
Data API v3 (`search.list`, `videos.list`, `channels.list`) via a bundled
script, so results are exact numbers straight from the API rather than
scraped or estimated.

## Inputs

The only thing the user is required to give you is the **search term** (the
topic/niche). Everything else has a sensible default, and you should state
the defaults you're using up front so the user can redirect you if they
actually wanted something different:

| Parameter | Default | Notes |
|---|---|---|
| Minimum views | 100,000 | The "overperformance" floor |
| Maximum subscribers | 100,000 | Keeps results to small/mid channels |
| Minimum views : subscribers ratio | 5 : 1 | The core "punching above their weight" signal |
| Number of candidates to find | 5 | Stop once you hit this many |
| Max search pages | 5 | Quota safety cap — see Quota below |

If the user gives you different numbers, use theirs instead. If the script
exhausts search results or hits the search-page cap before reaching the
requested count, report however many qualifying videos it actually found —
don't re-run with ever-looser queries trying to force a full set.

## Getting an API key

If the user doesn't already have `YOUTUBE_API_KEY` set (see Tooling below),
walk them through this rather than assuming they know it:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and
   create a project (or pick an existing one).
2. Enable the **YouTube Data API v3** for that project.
3. Go to **APIs & Services → Credentials → Create Credentials → API key**.
4. Optionally restrict the key to the YouTube Data API v3 (recommended, but
   not required for this to work).

Google's own walkthrough covers this in more detail:
[Registering an application (YouTube Data API)](https://developers.google.com/youtube/registering_an_application).

**Cost**: this is free. No billing account or credit card is required for
the default quota — Google caps it at 10,000 quota units/day per project,
which resets daily. A typical run of this skill (search + candidate lookups)
costs roughly 200–550 units depending on how many search pages it needs
(observed: ~510 units for a 5-page run), so the daily quota comfortably
covers dozens of runs before you'd ever hit the cap.

**Setting the key as an environment variable**:

- macOS/Linux (zsh, the default on modern macOS): add it to `~/.zshenv`
  (this file is sourced for every shell, including non-interactive ones
  that scripts run under, so it's more reliable here than `~/.zshrc`):
  ```
  export YOUTUBE_API_KEY="your-key-here"
  ```
  Then open a new terminal, or run `source ~/.zshenv` in the current one.
- Windows: in PowerShell, run:
  ```
  setx YOUTUBE_API_KEY "your-key-here"
  ```
  `setx` persists it for future sessions but not the current one — close and
  reopen the terminal (or restart the app running Claude) before it takes
  effect. Alternatively, set it via **System Properties → Environment
  Variables** in the Windows GUI.

## Tooling

This requires `YOUTUBE_API_KEY` to be set in the environment (see Getting an
API key above) and the YouTube Data API v3 to be enabled for that key's
Google Cloud project. If a call fails because the key is missing or
invalid, or the key's quota is exhausted, the script reports this clearly on
stderr with a non-zero exit — relay that message to the user rather than
attempting a workaround (there is no scraping fallback anymore).

Run the script with Bash:

```
python3 ~/.claude/skills/youtube-idea-finder/scripts/youtube_idea_finder.py \
  --query "<search term>" \
  --min-views <N> --max-subs <N> --min-ratio <N> --count <N> --max-pages <N>
```

It prints one JSON object to stdout:

```json
{
  "query": "...",
  "thresholds": {"min_views": ..., "max_subs": ..., "min_ratio": ..., "count": ...},
  "candidates": [
    {
      "title": "...", "video_id": "...", "url": "...",
      "views": 0, "channel_id": "...", "channel_title": "...",
      "subscribers": 0, "ratio": 0.0
    }
  ],
  "pages_searched": 0,
  "quota_used_estimate": 0,
  "stopped_reason": "reached_count | max_pages_reached | results_exhausted"
}
```

`candidates` is already filtered against all thresholds, Shorts-excluded, and
sorted by ratio descending — you don't need to re-check the numbers, just
format them (see Output format below).

## Quota

`search.list` costs 100 quota units per page (50 results); `videos.list` and
`channels.list` cost 1 unit per call regardless of batch size (up to 50 IDs
batched per call). The default free quota is 10,000 units/day, so search
pages are the only part worth budgeting — the script defaults to
`--max-pages 5` (≈500 units, ~510 observed in practice) so one run can't
consume the whole daily quota. Mention `quota_used_estimate` from the result
if the user seems to be running this repeatedly in a day, so they can judge
how much headroom is left.

Raise `--max-pages` only if the user explicitly asks for a broader search or
a larger `--count` than 5 pages is likely to satisfy — don't raise it
speculatively.

## Shorts handling

The API has no official "is this a Short" field. The script filters using
`contentDetails.duration`: any video ≤3 minutes is treated as a Short and
discarded before it ever reaches the candidate list, matching YouTube's own
Shorts duration ceiling. This is a heuristic, not a certainty — if a
result's legitimacy is in doubt (e.g. the user questions a specific result),
you can spot-check by opening `https://www.youtube.com/watch?v=<video_id>`
or noting the duration next to the title, but don't re-verify every
candidate by default; the script already applied this filter to everything
it returned.

## Workflow

### 1. Post a quick overview before running the script

State the search term and the thresholds you'll apply (say plainly whether
each is the default from the table above or a number the user gave you).
Since a wrong assumption means re-running the search (and spending quota
again), it's worth a beat to confirm before running.

### 2. Run the script

Invoke it via Bash with the query and thresholds. If it exits non-zero,
relay the stderr message directly — don't retry blindly or invent a
workaround.

### 3. Report the results

Take the `candidates` array from the JSON output and present it as the table
below. If `stopped_reason` is `"max_pages_reached"` or `"results_exhausted"`
and fewer candidates were found than requested, say so explicitly rather
than silently returning a shorter list. If `"max_pages_reached"`, mention
that raising `--max-pages` (at the cost of more quota) could turn up more.

## Output format

Report results as a markdown table, most-notable (highest ratio) first:

| Title | Views | Subscribers | Channel | Ratio | Link |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ...:1 | [link](...) |

Briefly note any thresholds you used that weren't explicitly stated by the
user, and if you stopped short of the requested count, say so plainly along
with the reason (`results_exhausted` vs `max_pages_reached`).
