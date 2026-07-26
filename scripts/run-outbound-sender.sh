#!/bin/zsh
set -euo pipefail

project_dir="$(cd "$(dirname "$0")/.." && pwd)"
state_dir="${EASTBAY_OUTBOUND_STATE:-$HOME/.local/share/eastbayprojects/outbound-sender}"
mkdir -p "$state_dir"
chmod 700 "$state_dir"

if [[ -f "$state_dir/service.env" ]]; then
  set -a
  source "$state_dir/service.env"
  set +a
fi

exec /opt/homebrew/bin/uv run --quiet \
  --with google-api-python-client \
  --with google-auth \
  python "$project_dir/outbound_sender/sender.py" "$@"
