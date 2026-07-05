#!/bin/bash
# Ensures the `markitdown` CLI is installed and on PATH, installing it via
# Homebrew + pipx if it's missing. Safe to run every time; it's a no-op if
# markitdown is already available.
#
# IMPORTANT: this script is meant to be *sourced* (not executed) so that a
# PATH fix survives into the caller's shell — e.g.
#   source ensure_markitdown.sh && markitdown foo.pdf -o foo.md
# Because of that, it must never call a plain `exit`: exiting from a sourced
# script terminates the *caller's* shell too, silently skipping whatever
# came after `&&`. Fatal errors use `return`, which unwinds just this
# script; if it's ever run standalone instead of sourced, `return` falls
# back to `exit` via the `|| exit 1` guard below.
set -uo pipefail

fatal() {
    echo "ERROR: $1" >&2
    return 1 2>/dev/null || exit 1
}

_markitdown_available() {
    if command -v markitdown >/dev/null 2>&1; then
        return 0
    fi
    if [ -x "$HOME/.local/bin/markitdown" ]; then
        # Some shells (e.g. non-login/non-interactive sessions) don't have
        # ~/.local/bin on PATH even when markitdown is genuinely installed
        # there — fix it up rather than reinstalling.
        export PATH="$HOME/.local/bin:$PATH"
        return 0
    fi
    return 1
}

if ! _markitdown_available; then
    echo "markitdown not found — installing via Homebrew + pipx..." >&2

    if ! command -v brew >/dev/null 2>&1; then
        fatal "Homebrew is required but not installed. Install it from https://brew.sh and re-run."
    fi

    brew install python@3.12 pipx

    PYTHON312="$(brew --prefix python@3.12)/bin/python3.12"
    pipx install "markitdown[all]" --python "$PYTHON312"
    pipx ensurepath

    export PATH="$HOME/.local/bin:$PATH"

    if ! command -v markitdown >/dev/null 2>&1; then
        fatal "markitdown installed but still not found on PATH."
    fi

    echo "markitdown installed successfully." >&2
fi
