#!/bin/zsh
set -euo pipefail
state="${EASTBAY_AD_REVIEW_STATE:-$HOME/.local/share/eastbayprojects/ad-review}"
mkdir -p "$state"
chmod 700 "$state"
if [[ -f "$state/service.env" ]]; then
  set -a
  source "$state/service.env"
  set +a
fi
exec /usr/bin/python3 "$(cd "$(dirname "$0")/.." && pwd)/ad_review/app.py"
