#!/usr/bin/env python3
"""
Fetch YouTube storyboard sprite frames (scrub-bar hover-preview images) at a
set of timestamps, for use by the youtube-video-evaluator skill's editing-
quality check. Browser-free: pulls static sprite sheet images via yt-dlp
metadata + direct HTTP fetch, then crops the requested cells with ffmpeg.
No video playback involved, so it can't be affected by a browser tab failing
to buffer real stream data.

Requires yt-dlp and ffmpeg on PATH (brew install yt-dlp; ffmpeg is usually
already present).

Usage:
  python3 fetch_storyboard_frames.py --url https://www.youtube.com/watch?v=ID \
    --checkpoints 0,45,90 --out-dir ./yt_eval/storyboards/ID

Crops one JPEG per checkpoint into --out-dir, named
checkpoint_<requested>s_actual<sampled>s.jpg (storyboard sampling is sparse,
so the actual sampled time rarely lands exactly on the requested second).
Prints a JSON summary to stdout; progress and storyboard-level details go to
stderr.
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request


class StoryboardError(Exception):
    pass


def run_ytdlp_json(url):
    try:
        proc = subprocess.run(
            ["yt-dlp", "-J", "--no-warnings", url],
            capture_output=True, text=True, timeout=60, check=True,
        )
    except FileNotFoundError as e:
        raise StoryboardError(
            "yt-dlp not found on PATH. Install it and try again -- see this "
            "skill's README (Prerequisites) for OS-specific steps."
        ) from e
    except subprocess.TimeoutExpired as e:
        raise StoryboardError("yt-dlp timed out fetching metadata") from e
    except subprocess.CalledProcessError as e:
        raise StoryboardError(f"yt-dlp exited {e.returncode}: {e.stderr[:500]}") from e
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise StoryboardError(f"Could not parse yt-dlp JSON output: {e}") from e


def extract_storyboard_formats(info):
    sbs = [f for f in info.get("formats", []) if f.get("format_note") == "storyboard"]
    if not sbs:
        raise StoryboardError(
            "No storyboard formats found for this video. Fall back to the "
            "browser-based playback check for this one candidate."
        )
    # Sort by resolution (cell width), not by format_id -- empirically sb0 is
    # highest-res and sb3 is lowest-res, the opposite of what the id ordering
    # suggests.
    sbs.sort(key=lambda f: f.get("width", 0))
    return sbs


def fetch_fragment_bytes(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        raise StoryboardError(f"Failed to fetch storyboard fragment: {e}") from e


def locate_checkpoint(storyboard, checkpoint_sec):
    fragments = storyboard["fragments"]
    fps = storyboard["fps"]
    rows, cols = storyboard["rows"], storyboard["columns"]
    frames_per_fragment = rows * cols
    sec_per_frame = 1.0 / fps

    elapsed = 0.0
    for idx, frag in enumerate(fragments):
        frag_dur = frag.get("duration", frames_per_fragment * sec_per_frame)
        if checkpoint_sec < elapsed + frag_dur or idx == len(fragments) - 1:
            offset_in_frag = checkpoint_sec - elapsed
            frame_idx = round(offset_in_frag / sec_per_frame)
            frame_idx = max(0, min(frame_idx, frames_per_fragment - 1))
            row, col = divmod(frame_idx, cols)
            actual_time = elapsed + frame_idx * sec_per_frame
            return idx, row, col, actual_time
        elapsed += frag_dur
    raise StoryboardError(f"Checkpoint {checkpoint_sec}s is beyond all fragments")


def crop_cell_with_ffmpeg(sprite_path, cell_w, cell_h, row, col, out_path):
    x, y = col * cell_w, row * cell_h
    cmd = [
        "ffmpeg", "-y", "-i", sprite_path,
        "-vf", f"crop={cell_w}:{cell_h}:{x}:{y}",
        "-frames:v", "1", out_path,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise StoryboardError(f"ffmpeg crop failed: {proc.stderr[-500:]}")


def fetch_frames(url, checkpoints, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    info = run_ytdlp_json(url)
    storyboards = extract_storyboard_formats(info)

    print(f"Found {len(storyboards)} storyboard levels (sorted low-res to high-res):", file=sys.stderr)
    for i, sb in enumerate(storyboards):
        print(f"  [{i}] {sb['format_id']}: {sb['width']}x{sb['height']} cell, "
              f"{sb['rows']}x{sb['columns']} grid, fps={sb['fps']:.4f}, "
              f"{len(sb['fragments'])} fragment(s)", file=sys.stderr)

    chosen = storyboards[-1]  # highest resolution
    print(f"Using storyboard {chosen['format_id']} ({chosen['width']}x{chosen['height']})", file=sys.stderr)

    frag_cache = {}
    frames = []
    for cp in checkpoints:
        frag_idx, row, col, actual_time = locate_checkpoint(chosen, cp)
        if frag_idx not in frag_cache:
            frag_url = chosen["fragments"][frag_idx]["url"]
            print(f"Fetching fragment {frag_idx}...", file=sys.stderr)
            data = fetch_fragment_bytes(frag_url)
            sprite_path = os.path.join(out_dir, f"sprite_frag{frag_idx}.jpg")
            with open(sprite_path, "wb") as f:
                f.write(data)
            frag_cache[frag_idx] = sprite_path
        sprite_path = frag_cache[frag_idx]

        out_name = f"checkpoint_{int(cp)}s_actual{actual_time:.1f}s.jpg"
        out_path = os.path.join(out_dir, out_name)
        crop_cell_with_ffmpeg(sprite_path, chosen["width"], chosen["height"], row, col, out_path)
        print(f"  checkpoint {cp}s -> actual_time={actual_time:.1f}s -> {out_path}", file=sys.stderr)
        frames.append({
            "requested_checkpoint_sec": cp,
            "actual_sampled_sec": round(actual_time, 1),
            "frame_path": out_path,
        })

    return {
        "storyboard_used": chosen["format_id"],
        "cell_size": [chosen["width"], chosen["height"]],
        "out_dir": out_dir,
        "frames": frames,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", required=True, help="Full YouTube video URL")
    parser.add_argument("--checkpoints", default="0,45,90", help="Comma-separated seconds")
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    checkpoints = [float(x) for x in args.checkpoints.split(",")]

    try:
        summary = fetch_frames(args.url, checkpoints, args.out_dir)
    except StoryboardError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
