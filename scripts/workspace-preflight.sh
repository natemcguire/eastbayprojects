#!/bin/zsh
set -euo pipefail

expected_host="Nates-Mac-mini.local"
current_host="$(hostname)"

if [[ "$current_host" != "$expected_host" && "${EASTBAY_ALLOW_LOCAL:-0}" != "1" ]]; then
  cat >&2 <<EOF
East Bay Projects development is pinned to $expected_host.
Connect with:
  ssh nate@nates-mac-mini
Then work from:
  ~/Projects/eastbayprojects
Set EASTBAY_ALLOW_LOCAL=1 only when Nate explicitly authorizes a temporary exception.
EOF
  exit 2
fi

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Preflight stopped: the checkout has uncommitted changes." >&2
  git status --short >&2
  exit 3
fi

git fetch --quiet origin main

read -r ahead behind <<<"$(git rev-list --left-right --count HEAD...origin/main)"

if (( ahead > 0 && behind > 0 )); then
  echo "Preflight stopped: main has diverged from origin/main." >&2
  exit 4
fi

if (( ahead > 0 )); then
  echo "Preflight stopped: local main is $ahead commit(s) ahead. Push or reconcile it first." >&2
  exit 5
fi

if (( behind > 0 )); then
  git pull --ff-only origin main
fi

echo "Preflight OK: $current_host $(git rev-parse --short HEAD) matches origin/main."

