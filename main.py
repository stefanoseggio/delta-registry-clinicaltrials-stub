"""
ClinicalTrials.gov one-off sample puller (free stub).

Pulls one page of real trial records from the public ClinicalTrials.gov
API v2 (https://clinicaltrials.gov/api/v2/studies), no API key required,
and saves a small JSON sample to disk.

This is a ONE-OFF, single-run script. It does not schedule itself, does
not track changes between runs, and does not retry failed requests. See
the "What this doesn't do" section of README.md for the full list, and
https://apify.com/stefano_seggio/actor-24-clinical-trials-delta-engine
for the hosted version that adds those things.
"""

import json
import sys
from urllib.parse import urlencode

import requests

# Real endpoint used by the production actor's fetchSources.ts, confirmed
# live via GET https://clinicaltrials.gov/api/v2/version during that
# actor's development. Free, no auth, no key required.
CLINICALTRIALS_BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

# Condition/disease filter passed to ClinicalTrials.gov's query.cond
# parameter. Change this to search a different condition.
CONDITION = "non-small cell lung cancer"

# How many records to keep in the saved sample. This stub pulls a single
# page and truncates to this cap - it does not paginate.
SAMPLE_SIZE = 20

OUTPUT_FILE = "sample_output.json"


def fetch_one_page(condition: str) -> dict:
    """Fetch a single page of studies from ClinicalTrials.gov API v2."""
    params = {
        "query.cond": condition,
        "pageSize": str(SAMPLE_SIZE),
        "fields": (
            "protocolSection.identificationModule,"
            "protocolSection.statusModule,"
            "protocolSection.sponsorCollaboratorsModule,"
            "protocolSection.conditionsModule,"
            "protocolSection.designModule"
        ),
    }
    url = f"{CLINICALTRIALS_BASE_URL}?{urlencode(params)}"

    try:
        response = requests.get(url, timeout=30)
    except requests.exceptions.RequestException as exc:
        print(f"ERROR: request to ClinicalTrials.gov failed: {exc}")
        sys.exit(1)

    if not response.ok:
        print(f"ERROR: ClinicalTrials.gov API returned HTTP {response.status_code}: {response.text[:300]}")
        sys.exit(1)

    try:
        return response.json()
    except ValueError as exc:
        print(f"ERROR: response was not valid JSON: {exc}")
        sys.exit(1)


def extract_record(study: dict) -> dict:
    """Pull out the same fields the production actor's dataset uses,
    from the same protocolSection.* paths, using a single-run snapshot
    shape (no delta fields - see README for what that means)."""
    protocol = study.get("protocolSection", {})
    identification = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    sponsor = protocol.get("sponsorCollaboratorsModule", {})
    conditions_module = protocol.get("conditionsModule", {})
    design = protocol.get("designModule", {})

    nct_id = identification.get("nctId")

    return {
        "nct_id": nct_id,
        "source_url": f"https://clinicaltrials.gov/study/{nct_id}" if nct_id else None,
        "brief_title": identification.get("briefTitle"),
        "overall_status": status.get("overallStatus"),
        "last_update_post_date": status.get("lastUpdatePostDateStruct", {}).get("date"),
        "status_verified_date": status.get("statusVerifiedDate"),
        "lead_sponsor": sponsor.get("leadSponsor", {}).get("name"),
        "conditions": conditions_module.get("conditions", []),
        "phases": design.get("phases", []),
    }


def main() -> None:
    print(f"Fetching trials for condition='{CONDITION}' from {CLINICALTRIALS_BASE_URL} ...")
    payload = fetch_one_page(CONDITION)

    studies = payload.get("studies", [])
    sample = [extract_record(study) for study in studies[:SAMPLE_SIZE]]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(sample, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(sample)} record(s) to {OUTPUT_FILE}")
    if sample:
        print("First record:")
        print(json.dumps(sample[0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
