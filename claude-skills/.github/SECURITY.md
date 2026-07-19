# Security policy

## Reporting a vulnerability

If you find a security issue in any of the skills or scripts in this repository, please report it privately rather than opening a public issue.

The preferred way is GitHub's private vulnerability reporting:

1. Go to the [Security tab](https://github.com/ErickRamirezAU/claude-skills/security) of this repository.
2. Click **Report a vulnerability**.
3. Describe the issue, including steps to reproduce it and its potential impact.

This is a personal, unpaid open source project, so please be patient waiting for a response.

## Scope

This repository contains instruction files (`SKILL.md`) and helper scripts (Python, shell) that Claude runs on your own machine or in your own Claude environment. Relevant issues include, but aren't limited to:

- A script that could be tricked into running unintended commands.
- Instructions that could cause Claude to leak sensitive local data.
- Supply chain issues in a script's dependencies.

## Supported versions

This project doesn't use version numbers or releases. Security fixes are applied to the `main` branch only.
