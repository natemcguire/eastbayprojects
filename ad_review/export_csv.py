#!/usr/bin/env python3
"""Export private sync plan into Google Ads CSV format for bulk upload / Google Ads Editor."""

import csv
import json
import os
from pathlib import Path

def export_google_ads_csv():
    plan_file = Path(os.path.expanduser("~/.local/share/eastbayprojects/ad-review/sync/plan.json"))
    if not plan_file.exists():
        print(f"Error: {plan_file} not found. Run build_sync_plan.py first.")
        return

    with open(plan_file, "r") as f:
        plan = json.load(f)

    search_campaign = plan.get("text_search", {}).get("campaign", {})
    campaign_name = search_campaign.get("name", "East Bay Projects - Approved Search Ads")
    
    output_path = Path("ad_review/google_ads_bulk_upload.csv")

    headers = [
        "Action",
        "Campaign",
        "Ad Group",
        "Status",
        "Type",
        "Headline 1",
        "Headline 2",
        "Headline 3",
        "Headline 4",
        "Headline 5",
        "Headline 6",
        "Headline 7",
        "Headline 8",
        "Headline 9",
        "Headline 10",
        "Description 1",
        "Description 2",
        "Description 3",
        "Description 4",
        "Path 1",
        "Path 2",
        "Final URL",
        "Keyword",
        "Match Type"
    ]

    rows = []

    # Campaign level row
    rows.append({
        "Action": "Add",
        "Campaign": campaign_name,
        "Ad Group": "",
        "Status": "Paused",
        "Type": "Campaign",
        "Final URL": "",
        "Keyword": "",
        "Match Type": ""
    })

    # Ad Groups & Ads
    keywords_by_group = {
        "GovCon & Federal Contractor Websites": [
            ('"govcon website design"', "Phrase"),
            ('"federal contractor website"', "Phrase"),
            ('"govcon web development"', "Phrase"),
            ("[government contractor website]", "Exact"),
            ("[govcon web design]", "Exact"),
        ],
        "Defense Credibility & Recruiting": [
            ('"defense contractor website"', "Phrase"),
            ('"defense firm web design"', "Phrase"),
            ("[defense contractor web design]", "Exact"),
            ("[cleared recruitment website]", "Exact"),
        ],
        "DMV Senior-Led Delivery": [
            ('"nova web design agency"', "Phrase"),
            ('"dc web development firm"', "Phrase"),
            ('"northern virginia website design"', "Phrase"),
            ("[dc web design company]", "Exact"),
        ],
        "Website Modernization": [
            ('"website modernization company"', "Phrase"),
            ('"replace outdated website"', "Phrase"),
            ('"rebuild wordpress site"', "Phrase"),
            ("[website redesign for business]", "Exact"),
            ("[b2b website modernization]", "Exact"),
        ]
    }

    negative_keywords = [
        "free", "jobs", "career", "salary", "internship", "template", "wordpress theme", "diy", "cheap"
    ]

    for group in search_campaign.get("ad_groups", []):
        group_name = group.get("name", "")
        
        # Ad Group row
        rows.append({
            "Action": "Add",
            "Campaign": campaign_name,
            "Ad Group": group_name,
            "Status": "Paused",
            "Type": "Ad Group",
            "Final URL": "",
            "Keyword": "",
            "Match Type": ""
        })

        # RSAs in Ad Group
        for rsa in group.get("responsive_search_ads", []):
            headlines = rsa.get("headlines", [])
            descriptions = rsa.get("descriptions", [])
            display_paths = rsa.get("display_paths", [])

            ad_row = {
                "Action": "Add",
                "Campaign": campaign_name,
                "Ad Group": group_name,
                "Status": "Paused",
                "Type": "Responsive search ad",
                "Headline 1": headlines[0] if len(headlines) > 0 else "",
                "Headline 2": headlines[1] if len(headlines) > 1 else "",
                "Headline 3": headlines[2] if len(headlines) > 2 else "",
                "Headline 4": headlines[3] if len(headlines) > 3 else "",
                "Headline 5": headlines[4] if len(headlines) > 4 else "",
                "Headline 6": headlines[5] if len(headlines) > 5 else "",
                "Headline 7": headlines[6] if len(headlines) > 6 else "",
                "Headline 8": headlines[7] if len(headlines) > 7 else "",
                "Headline 9": headlines[8] if len(headlines) > 8 else "",
                "Headline 10": headlines[9] if len(headlines) > 9 else "",
                "Description 1": descriptions[0] if len(descriptions) > 0 else "",
                "Description 2": descriptions[1] if len(descriptions) > 1 else "",
                "Description 3": descriptions[2] if len(descriptions) > 2 else "",
                "Description 4": descriptions[3] if len(descriptions) > 3 else "",
                "Path 1": display_paths[0] if len(display_paths) > 0 else "",
                "Path 2": display_paths[1] if len(display_paths) > 1 else "",
                "Final URL": rsa.get("final_urls", ["https://eastbayprojects.com/contact"])[0],
                "Keyword": "",
                "Match Type": ""
            }
            rows.append(ad_row)

        # Keywords for Ad Group
        if group_name in keywords_by_group:
            for kw, match_type in keywords_by_group[group_name]:
                rows.append({
                    "Action": "Add",
                    "Campaign": campaign_name,
                    "Ad Group": group_name,
                    "Status": "Enabled",
                    "Type": "Keyword",
                    "Final URL": "",
                    "Keyword": kw.strip('[]"'),
                    "Match Type": match_type
                })

    # Negative Keywords
    for neg in negative_keywords:
        rows.append({
            "Action": "Add",
            "Campaign": campaign_name,
            "Ad Group": "",
            "Status": "Enabled",
            "Type": "Negative Keyword",
            "Final URL": "",
            "Keyword": neg,
            "Match Type": "Phrase"
        })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Successfully generated Google Ads Bulk Export CSV: {output_path} ({len(rows)} rows)")

if __name__ == "__main__":
    export_google_ads_csv()
