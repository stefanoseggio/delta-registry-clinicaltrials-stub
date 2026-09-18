# ClinicalTrials.gov Sample Puller (free, one-off)

This is a free, open-source, one-off sample puller for ClinicalTrials.gov. It calls the public [ClinicalTrials.gov API v2](https://clinicaltrials.gov/data-api/api) (`GET https://clinicaltrials.gov/api/v2/studies`), fetches a single page of trials matching a condition filter, and saves up to 20 of them as a local JSON file. It is a plain local script, not a scheduled or hosted service: run it, get one snapshot, done. It does not remember anything between runs and does not tell you what changed - for that, see the paid actor linked at the bottom.

## Setup and run

```bash
pip install -r requirements.txt
python main.py
```

No API key or account is required - ClinicalTrials.gov's API v2 is free and unauthenticated. By default the script searches for `"non-small cell lung cancer"` (set in the `CONDITION` constant near the top of `main.py`); edit that constant to search a different condition. Output is written to `sample_output.json` in the current directory.

## Example output

This is real output from an actual run against the live API (`sample_output.json`, first record shown):

```json
{
  "nct_id": "NCT03526900",
  "source_url": "https://clinicaltrials.gov/study/NCT03526900",
  "brief_title": "Atezolizumab in Combination With Carboplatin Plus Pemetrexed in Chemotherapy-naïve Patients With Asymptomatic Brain Metastasis",
  "overall_status": "COMPLETED",
  "last_update_post_date": "2024-10-09",
  "status_verified_date": "2024-10",
  "lead_sponsor": "Spanish Lung Cancer Group",
  "conditions": [
    "Non-small Cell Lung Cancer Stage IV"
  ],
  "phases": [
    "PHASE2"
  ]
}
```

Field names (`nct_id`, `overall_status`, `last_update_post_date`, `status_verified_date`, `lead_sponsor`, `conditions`, `phases`) match the production actor's dataset schema, pulled from the same `protocolSection.identificationModule` / `statusModule` / `sponsorCollaboratorsModule` / `conditionsModule` / `designModule` paths in the raw API response.

## What this doesn't do

This stub is intentionally simple. It does **not**:

- **Schedule itself.** It runs once, when you run it, and exits. There's no cron, no recurring trigger, no "check again tomorrow."
- **Track changes (delta detection).** Every run is a cold, stateless snapshot. It has no memory of a previous run, so it can't tell you that a trial's `overallStatus` moved from `RECRUITING` to `TERMINATED` - it can only show you today's value.
- **Retry failed requests.** If the HTTP request fails or the API returns a non-2xx status, the script prints an error and exits. No backoff, no re-attempt.
- **Dead-letter failed pages.** There's no queue of failed fetches to inspect or replay - a failure is just a failure.
- **Paginate beyond one page.** It fetches a single page (capped at 20 records) and stops, rather than walking multiple pages of results.

These are the real, genuine gaps between this free stub and a production monitoring pipeline - not artificial limitations.

## Need scheduling, delta-tracking, and reliability?

For scheduled runs, delta/change-tracking, and reliability guarantees, see the production actor: https://apify.com/stefano_seggio/actor-24-clinical-trials-delta-engine

## License

MIT — see [LICENSE](LICENSE).
