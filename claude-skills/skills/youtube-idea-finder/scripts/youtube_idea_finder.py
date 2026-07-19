#!/usr/bin/env python3
"""
Find YouTube videos that overperform relative to their channel's subscriber
count, using the YouTube Data API v3 (search.list + videos.list +
channels.list) instead of browser scraping.

Requires YOUTUBE_API_KEY in the environment.

Usage:
  python3 youtube_idea_finder.py --query "sourdough bread baking" \
      [--min-views 100000] [--max-subs 100000] [--min-ratio 5.0] \
      [--count 5] [--max-pages 5]

Prints a single JSON object to stdout (see build_result()) and exits
non-zero on a hard error (missing key, quota exceeded, network failure).
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

API_BASE = "https://www.googleapis.com/youtube/v3"
SHORTS_MAX_SECONDS = 180  # matches the ~3 minute Shorts threshold
BATCH_SIZE = 50  # max IDs per videos.list / channels.list call

SEARCH_COST = 100
LIST_COST = 1

DURATION_RE = re.compile(
    r"^PT(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?$"
)


class ApiError(Exception):
    pass


def parse_duration_seconds(iso8601):
    match = DURATION_RE.match(iso8601 or "")
    if not match:
        return None
    hours = int(match.group("hours") or 0)
    minutes = int(match.group("minutes") or 0)
    seconds = int(match.group("seconds") or 0)
    return hours * 3600 + minutes * 60 + seconds


def api_get(api_key, endpoint, params):
    query = dict(params)
    query["key"] = api_key
    url = f"{API_BASE}/{endpoint}?{urllib.parse.urlencode(query)}"
    try:
        with urllib.request.urlopen(url) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            reason = json.loads(body)["error"]["errors"][0]["reason"]
        except (KeyError, IndexError, json.JSONDecodeError):
            reason = body[:200]
        if reason in ("quotaExceeded", "dailyLimitExceeded"):
            raise ApiError(
                "YouTube API quota exceeded for today. Try again after the "
                "daily quota resets, or request a quota increase in Google "
                "Cloud Console."
            ) from e
        if reason in ("keyInvalid", "badRequest") or e.code in (400, 403):
            raise ApiError(
                f"YouTube API rejected the request ({reason}). Check that "
                "YOUTUBE_API_KEY is set and the YouTube Data API v3 is "
                "enabled for its Google Cloud project."
            ) from e
        raise ApiError(f"YouTube API error ({e.code}): {reason}") from e
    except urllib.error.URLError as e:
        raise ApiError(f"Network error calling YouTube API: {e.reason}") from e


def chunked(items, size):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def search_videos_page(api_key, query, page_token):
    params = {
        "part": "snippet",
        "type": "video",
        "q": query,
        "maxResults": BATCH_SIZE,
        "safeSearch": "none",
    }
    if page_token:
        params["pageToken"] = page_token
    data = api_get(api_key, "search", params)
    items = [
        {
            "video_id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "channel_id": item["snippet"]["channelId"],
        }
        for item in data.get("items", [])
        if item.get("id", {}).get("videoId")
    ]
    return items, data.get("nextPageToken")


def get_video_stats(api_key, video_ids):
    stats = {}
    calls = 0
    for batch in chunked(video_ids, BATCH_SIZE):
        data = api_get(
            api_key,
            "videos",
            {"part": "statistics,contentDetails", "id": ",".join(batch)},
        )
        calls += 1
        for item in data.get("items", []):
            stats[item["id"]] = {
                "views": int(item["statistics"].get("viewCount", 0)),
                "duration_seconds": parse_duration_seconds(
                    item["contentDetails"].get("duration")
                ),
            }
    return stats, calls


def get_channel_stats(api_key, channel_ids):
    stats = {}
    calls = 0
    for batch in chunked(channel_ids, BATCH_SIZE):
        data = api_get(
            api_key,
            "channels",
            {"part": "statistics,snippet", "id": ",".join(batch)},
        )
        calls += 1
        for item in data.get("items", []):
            hidden = item["statistics"].get("hiddenSubscriberCount", False)
            stats[item["id"]] = {
                "title": item["snippet"].get("title"),
                "subscribers": (
                    None if hidden else int(item["statistics"].get("subscriberCount", 0))
                ),
            }
    return stats, calls


def find_candidates(api_key, query, min_views, max_subs, min_ratio, count, max_pages):
    qualifying = []
    seen_video_ids = set()
    channel_cache = {}
    pages_searched = 0
    quota_used = 0
    stopped_reason = "reached_count"

    page_token = None
    while len(qualifying) < count and pages_searched < max_pages:
        items, next_token = search_videos_page(api_key, query, page_token)
        pages_searched += 1
        quota_used += SEARCH_COST

        items = [i for i in items if i["video_id"] not in seen_video_ids]
        if not items:
            if not next_token:
                stopped_reason = "results_exhausted"
                break
            page_token = next_token
            continue

        video_stats, calls = get_video_stats(
            api_key, [i["video_id"] for i in items]
        )
        quota_used += calls * LIST_COST

        pending = []
        for item in items:
            seen_video_ids.add(item["video_id"])
            vstat = video_stats.get(item["video_id"])
            if not vstat:
                continue
            if vstat["views"] < min_views:
                continue
            duration = vstat["duration_seconds"]
            if duration is not None and duration <= SHORTS_MAX_SECONDS:
                continue  # likely a Short, discard regardless of numbers
            pending.append(
                {
                    "video_id": item["video_id"],
                    "title": item["title"],
                    "channel_id": item["channel_id"],
                    "views": vstat["views"],
                    "duration_seconds": duration,
                }
            )

        uncached_channel_ids = sorted(
            {p["channel_id"] for p in pending} - channel_cache.keys()
        )
        if uncached_channel_ids:
            new_stats, calls = get_channel_stats(api_key, uncached_channel_ids)
            quota_used += calls * LIST_COST
            channel_cache.update(new_stats)

        for p in pending:
            cstat = channel_cache.get(p["channel_id"])
            if not cstat or cstat["subscribers"] is None:
                continue  # channel hides subscriber count, can't compute ratio
            subs = cstat["subscribers"]
            if subs > max_subs or subs <= 0:
                continue
            ratio = p["views"] / subs
            if ratio < min_ratio:
                continue
            qualifying.append(
                {
                    "title": p["title"],
                    "video_id": p["video_id"],
                    "url": f"https://www.youtube.com/watch?v={p['video_id']}",
                    "views": p["views"],
                    "channel_id": p["channel_id"],
                    "channel_title": cstat["title"],
                    "subscribers": subs,
                    "ratio": round(ratio, 2),
                }
            )

        if not next_token:
            if len(qualifying) < count:
                stopped_reason = "results_exhausted"
            break
        page_token = next_token
    else:
        if len(qualifying) < count:
            stopped_reason = "max_pages_reached"

    qualifying.sort(key=lambda c: c["ratio"], reverse=True)
    return qualifying[:count], pages_searched, quota_used, stopped_reason


def build_result(query, thresholds, candidates, pages_searched, quota_used, stopped_reason):
    return {
        "query": query,
        "thresholds": thresholds,
        "candidates": candidates,
        "pages_searched": pages_searched,
        "quota_used_estimate": quota_used,
        "stopped_reason": stopped_reason,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True, help="Search term / niche topic")
    parser.add_argument("--min-views", type=int, default=100_000)
    parser.add_argument("--max-subs", type=int, default=100_000)
    parser.add_argument("--min-ratio", type=float, default=5.0)
    parser.add_argument("--count", type=int, default=5, help="Number of qualifying candidates to find")
    parser.add_argument(
        "--max-pages",
        type=int,
        default=5,
        help="Cap on search.list pages fetched (each page costs 100 quota units)",
    )
    args = parser.parse_args()

    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print(
            "Error: YOUTUBE_API_KEY is not set in the environment.",
            file=sys.stderr,
        )
        sys.exit(1)

    thresholds = {
        "min_views": args.min_views,
        "max_subs": args.max_subs,
        "min_ratio": args.min_ratio,
        "count": args.count,
    }

    try:
        candidates, pages_searched, quota_used, stopped_reason = find_candidates(
            api_key,
            args.query,
            args.min_views,
            args.max_subs,
            args.min_ratio,
            args.count,
            args.max_pages,
        )
    except ApiError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    result = build_result(
        args.query, thresholds, candidates, pages_searched, quota_used, stopped_reason
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
