#!/bin/bash
# Ensures the `markitdown` CLI is installed and on PATH, installing it if
# missing. Safe to run every time; it's a no-op if markitdown is already
# available.
#
# IMPORTANT: this script is meant to be *sourced* (not executed) so that a
# PATH fix survives into the caller's shell — e.g.
#   source ensure_markitdown.sh && markitdown foo.pdf -o foo.md
# Because of that, it must never call a plain `exit`: exiting from a sourced
# script terminates the *caller's* shell too, silently skipping whatever
# came after `&&`. Fatal errors use `return`, which unwinds just this
# script; if it's ever run standalone instead of sourced, `return` falls
# back to `exit` via the `|| exit 1` guard below.
#
# Platform notes:
# - macOS: uses Homebrew + pipx, the reliable standard there.
# - Linux: prefers pipx/pip3/pip directly — no Homebrew dependency, since
#   most Linux users won't have it installed.
# - Windows under WSL reports as Linux via `uname`, so it's covered by the
#   Linux path above with no special-casing needed.
# - Windows *without* WSL (Git Bash/MSYS/Cygwin) is its own case below: the
#   console-script executable often isn't named `python3`, and pip installs
#   scripts to `%APPDATA%\Python\PythonXY\Scripts`, not `~/.local/bin`.
set -uo pipefail

fatal() {
    echo "ERROR: $1" >&2
    return 1 2>/dev/null || exit 1
}

# Finds a working Python interpreter command, trying the names most likely
# to exist on each platform in order. Echoes the command (possibly two
# words, e.g. "py -3") on success.
_find_python() {
    if command -v python3 >/dev/null 2>&1; then
        echo "python3"
        return 0
    fi
    if command -v python >/dev/null 2>&1; then
        echo "python"
        return 0
    fi
    # The `py` launcher is the standard entrypoint on native Windows Python
    # installs when neither `python3` nor `python` is on PATH.
    if command -v py >/dev/null 2>&1; then
        echo "py -3"
        return 0
    fi
    return 1
}

# Common locations pip installs console scripts to on native Windows when
# using python.org/Microsoft Store Python with `pip install --user`.
_windows_scripts_dirs() {
    if [ -n "${APPDATA:-}" ]; then
        for d in "$APPDATA"/Python/Python*/Scripts; do
            [ -d "$d" ] && echo "$d"
        done
    fi
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
    while IFS= read -r d; do
        if [ -x "$d/markitdown.exe" ] || [ -x "$d/markitdown" ]; then
            export PATH="$d:$PATH"
            return 0
        fi
    done < <(_windows_scripts_dirs)
    # Broader check: markitdown can be importable as a Python module even
    # when its console-script entrypoint isn't on PATH or in a location
    # above — e.g. installed inside a venv, via a system package manager,
    # or with a non-standard `pip install --target`. If so, use the module
    # invocation for the rest of this shell instead of assuming it's
    # missing entirely.
    PYTHON_CMD="$(_find_python 2>/dev/null || true)"
    if [ -n "${PYTHON_CMD:-}" ] && $PYTHON_CMD -c "import markitdown" >/dev/null 2>&1; then
        eval "markitdown() { $PYTHON_CMD -m markitdown \"\$@\"; }"
        export -f markitdown 2>/dev/null || true
        return 0
    fi
    return 1
}

if ! _markitdown_available; then
    echo "markitdown not found — installing..." >&2

    case "$(uname -s)" in
        Darwin)
            # Homebrew is the reliable, standard path on macOS.
            if ! command -v brew >/dev/null 2>&1; then
                fatal "Homebrew is required but not installed on macOS. Install it from https://brew.sh and re-run, or install markitdown yourself with: pip install \"markitdown[all]\""
            fi
            brew install python@3.12 pipx
            PYTHON312="$(brew --prefix python@3.12)/bin/python3.12"
            pipx install "markitdown[all]" --python "$PYTHON312"
            pipx ensurepath
            export PATH="$HOME/.local/bin:$PATH"
            ;;
        MINGW*|MSYS*|CYGWIN*)
            # Native Windows (Git Bash/MSYS/Cygwin, not WSL). No Homebrew,
            # and pip's --user scripts land under %APPDATA%, not ~/.local/bin.
            PYTHON_CMD="$(_find_python)" || fatal "No Python found. Install it from https://python.org (check \"Add python.exe to PATH\" during setup) and re-run, or install markitdown yourself with: pip install \"markitdown[all]\""
            if command -v pipx >/dev/null 2>&1; then
                pipx install "markitdown[all]"
                pipx ensurepath
            else
                $PYTHON_CMD -m pip install --user "markitdown[all]"
            fi
            while IFS= read -r d; do
                export PATH="$d:$PATH"
            done < <(_windows_scripts_dirs)
            export PATH="$HOME/.local/bin:$PATH"
            ;;
        *)
            # Linux (including WSL) and other Unix-likes: pip/pipx are
            # near-universal, so prefer those rather than demanding a
            # macOS-flavored dependency.
            if command -v pipx >/dev/null 2>&1; then
                pipx install "markitdown[all]"
                pipx ensurepath
            elif command -v pip3 >/dev/null 2>&1; then
                pip3 install --user "markitdown[all]"
            elif command -v pip >/dev/null 2>&1; then
                pip install --user "markitdown[all]"
            else
                fatal "No pip or pipx found. Install Python's pip (e.g. 'sudo apt install python3-pip' on Debian/Ubuntu) and re-run, or install markitdown yourself with: pip install \"markitdown[all]\""
            fi
            export PATH="$HOME/.local/bin:$PATH"
            ;;
    esac

    if ! _markitdown_available; then
        fatal "markitdown installed but still not found on PATH."
    fi

    echo "markitdown installed successfully." >&2
fi
