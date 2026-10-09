# PagerDuty Incident Resolver

## Overview
This tool automatically resolves PagerDuty incidents that meet specific criteria. It fetches incidents from the PagerDuty API, filters them based on predefined conditions, and updates their status to "resolved".

## Scope
- **Fetches** all incidents from PagerDuty API (with automatic pagination)
- **Filters** incidents that match ALL of the following conditions:
  - Status is `"triggered"`
  - Service ID matches the configured service ID
- **Updates** matching incidents to `"resolved"` status
- **Handles** hundreds of incidents with rate limiting
- **Reports** summary of successful and failed updates

## Requirements
- Python 3.6 or higher
- No external dependencies (uses built-in libraries only)

## Installation

1. Configure your API credentials in `config.json` (see Configuration section below)

## Configuration

Edit the `config.json` file with your PagerDuty credentials:

```json
{
  "api_key": "your_pagerduty_api_token_here",
  "user_email": "your.email@company.com",
  "service_id": "POM9BPX",
  "rate_limit_delay": 0.5
}
```

**Configuration Parameters:**
- `api_key`: Your PagerDuty API token (required for authentication)
- `user_email`: Email address of the user resolving incidents (must have a PagerDuty account)
- `service_id`: The PagerDuty service ID to filter incidents (e.g., "POM9BPX")
- `rate_limit_delay`: Delay in seconds between PUT requests to avoid rate limiting (default: 0.5)

## Usage

Run the script:
```bash
python resolve_incidents.py
```

The script will:
1. Load configuration from `config.json`
2. Fetch all incidents from PagerDuty (handles pagination automatically)
3. Filter incidents matching the criteria (status="triggered" AND service_id matches config)
4. Update each matching incident to "resolved"
5. Display a summary report

## Output

The script provides a summary report showing:
- Total incidents fetched
- Number of incidents matching filter criteria
- Number of successfully resolved incidents
- List of failed incidents (if any) with error details

### Example Output:
```
=== PagerDuty Incident Resolver ===
Fetching incidents from PagerDuty...
Fetched 150 total incidents across 6 pages

Filtering incidents (status='triggered', service_id='POM9BPX')...
Found 23 incidents matching criteria

Resolving incidents...
Progress: 23/23 incidents processed

=== Summary Report ===
Total incidents fetched: 150
Incidents matching criteria: 23
Successfully resolved: 22
Failed to resolve: 1

Failed Incidents:
- Q2K0N7MHJM16II: 403 Forbidden - User does not have permission
```

## Notes
- The script includes rate limiting to prevent API throttling
- Failed incidents will not stop the script from processing remaining incidents
- Ensure your API token has sufficient permissions to update incidents
- The user email must belong to a valid PagerDuty account

## Troubleshooting

**Authentication errors**: Verify your API token is correct in `config.json`

**Permission errors**: Ensure the user email has permissions to resolve incidents

**No incidents found**: Check that the service_id is correct and incidents exist with status="triggered"


---
**Setup:** edit `config.json` and replace the placeholder values with your own. Keep your real API key out of commits. Run with `dry_run` enabled first.
