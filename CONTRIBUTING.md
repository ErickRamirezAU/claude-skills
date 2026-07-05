# Contributing to claude-skills

Thanks for considering a contribution! You don't need to be a programmer — improving the plain-English wording in a `SKILL.md` file or a README is just as valuable as a code change.

## Reporting bugs or suggesting ideas

Open an issue describing what's wrong or what you'd like to see.

## Submitting a change

1. Fork this repository and create a new branch.
2. Make your change:
   - If you're editing an existing skill, try it with Claude first to confirm it still works as expected.
   - If you're adding a new skill, follow the layout used here: a folder under `skills/` containing a `SKILL.md` (instructions for Claude) and a `README.md` (usage instructions for humans — this is what GitHub displays when someone browses into the folder), plus any supporting `scripts/`.
3. Open a pull request describing what changed and why.

## Skill README style guide

Every skill's `README.md` should follow the same section order, so a reader who's used one skill in this repo already knows where to look in another. Only the first three are required — include the optional ones only if they apply.

**Required:**
1. `## What it does` — a plain-English description of the task.
2. `## Usage` — how to invoke it (a realistic example prompt), and what to expect back.
3. `## Sample output` — a real example (a prompt and the actual response it produced), not an invented one. If you don't have a real run to draw from, ask before publishing a fabricated one.

**Optional, include only if relevant, in this order:**

4. `## Limitations` — environments or scenarios where the skill doesn't work, using a `> [!WARNING]` callout for anything that would silently fail otherwise.
5. `## Prerequisites` — setup required before first use (API keys, installed tools, accounts).
6. `## Options` — configurable parameters, presented as a table of Option / Default / What it controls, mirroring the Inputs table in `SKILL.md` if one exists.
7. `## Troubleshooting` — skill-specific error messages and fixes. General install/setup issues belong in the top-level README instead.

Full order when all sections apply: What it does → Limitations → Prerequisites → Usage → Options → Sample output → Troubleshooting.
