#!/usr/bin/env python3
"""
Fetch YouTube video metadata and thumbnails for a batch of video IDs, for use
by the youtube-video-evaluator skill. Companion to youtube-idea-finder's own
script, but kept separate: this reads existing video IDs, it doesn't search.

Requires YOUTUBE_API_KEY in the environment (same variable the idea-finder
skill uses).

Usage:
  python3 fetch_video_metadata.py --ids ID1,ID2,ID3 --out-dir ./yt_eval
  python3 fetch_video_metadata.py --finder-json finder_output.json --out-dir ./yt_eval

Downloads each video's best-available thumbnail into <out-dir>/thumbnails/<id>.jpg
and prints a single JSON array to stdout, one object per video, in input order.
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
BATCH_SIZE = 50

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


def best_thumbnail(thumbnails):
    for key in ("maxres", "standard", "high", "medium", "default"):
        if key in thumbnails:
            return thumbnails[key]["url"]
    return None


def download_thumbnail(url, dest_path):
    try:
        with urllib.request.urlopen(url) as resp:
            data = resp.read()
        with open(dest_path, "wb") as f:
            f.write(data)
        return True
    except (urllib.error.URLError, urllib.error.HTTPError):
        return False


def fetch_metadata(api_key, video_ids, out_dir):
    thumb_dir = os.path.join(out_dir, "thumbnails")
    os.makedirs(thumb_dir, exist_ok=True)

    results = {}
    for batch in chunked(video_ids, BATCH_SIZE):
        data = api_get(
            api_key,
            "videos",
            {"part": "snippet,statistics,contentDetails", "id": ",".join(batch)},
        )
        for item in data.get("items", []):
            vid = item["id"]
            sn = item["snippet"]
            st = item["statistics"]
            cd = item["contentDetails"]
            thumb_url = best_thumbnail(sn.get("thumbnails", {}))
            thumb_path = None
            if thumb_url:
                candidate_path = os.path.join(thumb_dir, f"{vid}.jpg")
                if download_thumbnail(thumb_url, candidate_path):
                    thumb_path = candidate_path
            results[vid] = {
                "video_id": vid,
                "title": sn.get("title"),
                "description": sn.get("description"),
                "tags": sn.get("tags", []),
                "channel_title": sn.get("channelTitle"),
                "published_at": sn.get("publishedAt"),
                "duration_seconds": parse_duration_seconds(cd.get("duration")),
                "has_captions": cd.get("caption") == "true",
                "views": int(st.get("viewCount", 0)),
                "likes": int(st.get("likeCount", 0)) if "likeCount" in st else None,
                "comments": int(st.get("commentCount", 0)) if "commentCount" in st else None,
                "thumbnail_url": thumb_url,
                "thumbnail_local_path": thumb_path,
            }

    # Preserve input order; silently drop any id the API didn't return
    # (private/deleted videos) rather than failing the whole batch.
    return [results[v] for v in video_ids if v in results]


def load_ids_from_finder_json(path):
    with open(path) as f:
        data = json.load(f)
    return [c["video_id"] for c in data.get("candidates", [])]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ids", help="Comma-separated list of YouTube video IDs")
    parser.add_argument("--finder-json", help="Path to a youtube_idea_finder.py JSON output file")
    parser.add_argument("--out-dir", required=True, help="Directory to write thumbnails/ into")
    args = parser.parse_args()

    if not args.ids and not args.finder_json:
        print("Error: provide --ids or --finder-json", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("Error: YOUTUBE_API_KEY is not set in the environment.", file=sys.stderr)
        sys.exit(1)

    if args.finder_json:
        video_ids = load_ids_from_finder_json(args.finder_json)
    else:
        video_ids = [v.strip() for v in args.ids.split(",") if v.strip()]

    try:
        results = fetch_metadata(api_key, video_ids, args.out_dir)
    except ApiError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
