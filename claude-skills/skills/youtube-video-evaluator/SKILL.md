---
name: youtube-video-evaluator
description: "Evaluates a batch of YouTube video candidates (typically the output of the youtube-idea-finder skill) for thumbnail quality, editing quality, topics, tech/tools, and format, then turns each into a Replicate/Fix/Calendar-action brief. Use this after youtube-idea-finder has surfaced overperforming videos, whenever the user wants to know WHY a video worked so they can copy the parts that worked and avoid the parts that didn't, or asks to turn found video ideas into a content calendar. Does not search or filter videos itself — it takes a list of already-identified candidates and produces a downloadable Markdown diagnostic report."
---

# YouTube Idea Evaluator

Takes video candidates (usually from `youtube-idea-finder`) and produces an
actionable diagnostic report per video: what its thumbnail and editing
actually look like and why, what topics/tech/format it covers, and a
concrete "replicate this, fix that, do this for your own calendar" brief.

This skill does not search YouTube or apply any pass/fail filter — every
candidate handed to it gets a full write-up. The point isn't to find gaps to
exploit, it's to reverse-engineer what worked (and what didn't) well enough
to turn it into a content calendar entry.

**Do not modify `youtube-idea-finder`.** It stays a standalone skill. This
skill only consumes its output (or a manually supplied list of video IDs/URLs).

## Inputs

- A JSON output file from `youtube_idea_finder.py` (has a `candidates` array
  with `video_id` per entry), or
- A plain list of YouTube video IDs or URLs the user pastes in directly

If the user hasn't run the finder yet and asks for both in one request, run
the finder first, show its table, then feed its candidates into this skill.
The finder needs a search term/niche to run — if the user hasn't given one
(e.g. they just said "find me some video ideas and evaluate them"), ask for
it before invoking the finder. Don't guess a query on their behalf.

If a `--finder-json` file is supplied instead (e.g. from an earlier
session, or handed off without restating the query in this conversation),
read the search term for the output filename directly from that file's
top-level `query` field rather than relying on conversation context —
`youtube_idea_finder.py` always writes it there.

## Scope

- **In scope:** thumbnail quality, editing/pacing quality, topics covered,
  tech/tools named, format/framing, and what's replicable vs. what needs
  fixing.
- **Out of scope:** audio quality (no way to assess it reliably without
  actually listening, so don't guess at it or even flag it as unassessed,
  just leave it out entirely). Captions are also out of scope — nearly
  every candidate tested turns out to lack them, which makes it a
  non-differentiating, arbitrary check rather than a real signal; don't
  fetch, check, or mention captions anywhere in the workflow or report.
  Don't gate or rank candidates into skip/green-light tiers — every
  candidate gets the full write-up regardless of how good or bad its
  packaging is, since the goal is proven-demand topics to build a calendar
  from, not a shortlist of "easy wins."

## Workflow

### 1. Fetch metadata and thumbnails

Batch-fetch all candidates in one call with the bundled script (mirrors
`youtube_idea_finder.py`'s own API usage, same `YOUTUBE_API_KEY` env var):

```
python3 ~/.claude/skills/youtube-video-evaluator/scripts/fetch_video_metadata.py \
  --finder-json /path/to/finder_output.json \
  --out-dir /path/to/scratch/dir
```

Or with explicit IDs: `--ids ID1,ID2,ID3` instead of `--finder-json`.

This returns title, full description, tags, duration, view/like/comment
counts, and downloads each video's best-available thumbnail to
`<out-dir>/thumbnails/<id>.jpg`. Read each thumbnail file directly to view
it (you have vision) — never re-fetch thumbnails by hand with curl, and
never try to embed the image bytes into any deliverable (base64-encoding
images for a document or widget is slow and produces a bad experience;
describe what you see in words instead). Ignore the `has_captions` field in
its output — captions are out of scope (see Scope above).

### 2. Judge each thumbnail

Rate **Bad / Mediocre / Good** against:

- Bad: plain screen recording or default frame, generic stock imagery, a
  wall of text with no focal point, no face or a face that blends in, low
  contrast or hard-to-read fonts, no clear promise in 2 seconds
- Good: bold text with one clear hook word, a face with an expressive
  reaction (or, if no face, a visual that shows the payoff directly — e.g.
  a before/after icon metaphor, or an actual screenshot of the working
  output), high contrast, the payoff is obvious at a glance
- Mediocre: has a real hook or decent contrast but is missing the other
  elements, or executes the idea half-heartedly (e.g. legible but cluttered,
  or a clear hook let down by a weak visual)

Note *why* in one line, specific enough that the user knows exactly what to
avoid or copy, not just the label.

### 3. Judge editing quality from storyboard frames at 0s/45s/90s

Do not use claude-in-chrome or any browser-based playback for this step —
an earlier version of this skill relied on screenshotting the live
`<video>` element and repeatedly produced false "frozen cold open" findings
because the tab's video stream silently failed to buffer any real data
(`readyState` stuck at `0`, `buffered` empty) while still rendering a
static poster frame. That failure mode is indistinguishable from a real
frozen video in a screenshot, so it went undetected until caught and
verified against an independent source. Storyboards sidestep the problem
entirely: they're static sprite-sheet images YouTube generates for its own
scrub-bar preview, fetched over plain HTTP with no player and no playback
state to go wrong.

Fetch frames with the bundled script (requires `yt-dlp` — `brew install
yt-dlp` if missing — and `ffmpeg`, mirrors the metadata script's
conventions):

```
python3 ~/.claude/skills/youtube-video-evaluator/scripts/fetch_storyboard_frames.py \
  --url https://www.youtube.com/watch?v=VIDEO_ID \
  --checkpoints 0,45,90 \
  --out-dir /path/to/scratch/dir/storyboards/VIDEO_ID
```

This prints a JSON summary listing each checkpoint's actual sampled time
(storyboard sampling is roughly 1 frame per 1.5-2s, so it rarely lands on
the exact requested second) and the path to a cropped JPEG per checkpoint.
Read each cropped JPEG directly to view it. If a video has no storyboard
formats at all (rare), the script exits with a clear error — fall back to
describing editing quality as unassessed for that one video rather than
guessing, and say so in the report.

Rate **Bad / Mediocre / Good** against:

- Bad: the checkpoints show no real progression (same or near-identical
  frame at 0s/45s/90s, consistent with a genuinely static title card that
  long), full OS/browser chrome visible on a screen recording, rambling
  structure with no hook visible at 0s
- Good: clearly distinct content at each checkpoint showing real structural
  variety (e.g. talking head to screen-share, cuts to a diagram/B-roll,
  demo-first hook already visible at 0s), clean cropped capture
- Mediocre: real progression exists between checkpoints but composition is
  weak (e.g. raw uncropped screen recording with no zooms or host-cam
  presence), or a strong cold open that isn't sustained by the later
  checkpoints

Three sample points can't catch individual cuts or confirm exact pacing —
they establish gross content-type and macro-pacing (static vs. changing,
talking-head vs. screen-share vs. diagram), which is enough signal for this
rating. Don't claim a specific duration for a static stretch (e.g. "static
for the first 90 seconds") beyond what the sampled checkpoints actually
show — if 0s is static but 45s already shows real content, say the static
stretch ended sometime before 45s, not that it lasted 90 seconds.

### 4. Extract topics, tech/tools, and format

- **Topics**: pull from the description's chapter list when present, or
  from the video's own narrative structure if not
- **Tech/tools**: pull from API `tags` plus anything named on-screen or in
  the description (specific frameworks, libraries, platforms)
- **Format**: name the shape, not just "tutorial" — e.g. single-concept
  explainer, head-to-head comparison, hands-on build (basic/advanced),
  talking-head roadmap, whiteboard system-design walkthrough, news-jacking
  reaction to a recent release. The format is often what actually explains
  the view-to-subscriber ratio, more than production polish does — a short
  single-concept explainer or a comparison riding a trending keyword can
  outperform a narrower, better-produced project build by an order of
  magnitude. Say so when the pattern shows up.

### 5. Write the per-video brief

For every candidate, regardless of rating:

- **What to replicate**: specific, nameable techniques — title formulas,
  thumbnail construction, structural beats (agenda slides, demo-first
  hooks, branded stings, PiP webcam styling), even on videos with mediocre
  or bad packaging (the topic itself still proved demand, that's always
  replicable even when the execution isn't)
- **What to fix**: concrete weaknesses, specific enough to act on. Don't
  let a "Good" rating suppress this section — call out real gaps even on
  well-produced videos
- **Calendar action**: one line translating the above into a concrete next
  step sized for a content calendar entry

## Output format

A single Markdown file, filename **`Video Ideas - [search terms].md`**
(note the plural "Ideas"), saved in the user's current working directory
unless told otherwise. If evaluating a manually supplied list of IDs/URLs
with truly no `query` field to recover it from (see Inputs above), ask the
user what to name the file — don't ask if the term was recoverable from a
supplied finder JSON.

Before writing, check whether the resolved filename already exists in the
target directory. If it does, append `(1)`, `(2)`, etc. before the `.md`
extension (`Video Ideas - [search terms] (1).md`, then `(2)`, ...) and use
the first one that doesn't collide. Never overwrite an existing report and
never prompt the user to confirm an overwrite — this applies regardless of
whether the search term came from the user, from a finder JSON's `query`
field, or from asking the user directly.

Structure:

```markdown
# Video Ideas - [search terms]

| # | Title | Channel | Ratio | Format |
|---|---|---|---|---|
| 1 | [Title](url) | Channel | N.NN:1 | Format label |
...

---

## 1. [Title]

| Field | Detail |
|---|---|
| Channel | ... |
| Link | ... |
| Views / Subscribers / Ratio | ... |
| Format | ... |
| Topics | ... |
| Tech/tools | ... |
| Thumbnail | **Good/Mediocre/Bad.** One-line specific reason. |
| Editing | **Good/Mediocre/Bad.** One-line specific reason. |

**What to replicate:**
- ...

**What to fix:**
- ...

**Calendar action:** One line.

---

## 2. [Title]
...
```

Always bold the Good/Mediocre/Bad rating at the start of the Thumbnail and
Editing table cells — the prose reasoning alone reads as ambiguous without
it. Use a proper two-column table for each video's metadata block, not a
stack of bold key:value lines — loose lines with single newlines collapse
onto one line in rendered Markdown and become unreadable.

Default to the Markdown file as the deliverable. Only reach for a visual
card/widget presentation if the user explicitly asks for one — it's a
heavier, slower artifact and real images can't be embedded in it without a
costly base64 round-trip, so it ends up carrying less information than the
plain Markdown version anyway.

## If the finder returns fewer candidates than requested

Not this skill's problem to solve, but worth relaying: state plainly how
many were evaluated vs. requested and why (`max_pages_reached` vs.
`results_exhausted`, from the finder's own output), same as the finder
skill itself would.
