#!/usr/bin/env python3
"""Google Ads API & MCP Tool for East Bay Projects."""

import json
import os
import sys
from pathlib import Path

# Paths
STATE_DIR = Path(os.path.expanduser("~/.local/share/eastbayprojects/ad-review"))
CONFIG_PATH = STATE_DIR / "google-ads.yaml"
PLAN_PATH = STATE_DIR / "sync" / "plan.json"

TEMPLATE_CONFIG = """# Google Ads API Credentials Configuration
# Save this to ~/.local/share/eastbayprojects/ad-review/google-ads.yaml

developer_token: "INSERT_DEVELOPER_TOKEN_HERE"
client_id: "INSERT_OAUTH2_CLIENT_ID.apps.googleusercontent.com"
client_secret: "INSERT_OAUTH2_CLIENT_SECRET"
refresh_token: "INSERT_OAUTH2_REFRESH_TOKEN"
customer_id: "285-654-0835"
# login_customer_id: "MCC_MANAGER_CUSTOMER_ID_IF_APPLICABLE"
use_proto_plus: True
"""

def check_config():
    if not CONFIG_PATH.exists():
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            f.write(TEMPLATE_CONFIG)
        print(f"Created template config file at: {CONFIG_PATH}")
        print("Please populate developer_token, client_id, client_secret, and refresh_token.")
        return False
    return True

def sync_plan_to_google_ads():
    if not check_config():
        return

    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException

    print(f"Loading credentials from {CONFIG_PATH}...")
    try:
        client = GoogleAdsClient.load_from_storage(str(CONFIG_PATH))
    except Exception as e:
        print(f"Error loading google-ads.yaml: {e}")
        return

    if not PLAN_PATH.exists():
        print(f"Error: {PLAN_PATH} not found. Run build_sync_plan.py first.")
        return

    with open(PLAN_PATH, "r") as f:
        plan = json.load(f)

    customer_id = plan.get("display_pmax", {}).get("customer_id") or "2856540835"
    customer_id = customer_id.replace("-", "")

    print(f"Connected to Google Ads API for Customer ID: {customer_id}")
    # Perform GAQL verification query
    ga_service = client.get_service("GoogleAdsService")
    query = """
        SELECT
          campaign.id,
          campaign.name,
          campaign.status
        FROM campaign
        LIMIT 10
    """

    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        print("Successfully queried Google Ads API!")
        for row in response:
            print(f"- Campaign ID: {row.campaign.id}, Name: '{row.campaign.name}', Status: {row.campaign.status.name}")
    except GoogleAdsException as ex:
        print(f"Google Ads API Error: {ex}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        check_config()
    else:
        sync_plan_to_google_ads()
