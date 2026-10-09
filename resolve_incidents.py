import json
import time
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

def load_config():
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)

        # Validate required fields
        required_fields = ['api_key', 'user_email', 'service_id']
        missing_fields = [field for field in required_fields if not config.get(field)]

        if missing_fields:
            print(f"Error: Missing required fields in config.json: {', '.join(missing_fields)}")
            sys.exit(1)

        return config
    except FileNotFoundError:
        print("Error: config.json not found. Please create it with your API credentials.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: config.json is not valid JSON.")
        sys.exit(1)

def get_all_incidents(api_key):
    """Fetch all incidents from PagerDuty with pagination"""
    base_url = "https://api.pagerduty.com/incidents"

    all_incidents = []
    offset = 0
    limit = 100  # Max per page
    more = True
    page_count = 0

    print("Fetching incidents from PagerDuty...")

    while more:
        params = urlencode({
            'limit': limit,
            'offset': offset
        })
        url = f"{base_url}?{params}"

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Token token={api_key}',
            'Content-Type': 'application/json'
        }

        try:
            request = Request(url, headers=headers)
            with urlopen(request) as response:
                data = json.loads(response.read().decode('utf-8'))

            incidents = data.get('incidents', [])
            all_incidents.extend(incidents)

            more = data.get('more', False)
            offset += limit
            page_count += 1

        except HTTPError as e:
            error_msg = e.read().decode('utf-8')
            print(f"HTTP Error fetching incidents: {e.code} {e.reason}")
            print(f"Details: {error_msg}")
            sys.exit(1)
        except URLError as e:
            print(f"URL Error fetching incidents: {e.reason}")
            sys.exit(1)
        except Exception as e:
            print(f"Error fetching incidents: {e}")
            sys.exit(1)

    print(f"Fetched {len(all_incidents)} total incidents across {page_count} pages\n")
    return all_incidents

def filter_incidents(incidents, service_id):
    """Filter incidents based on status='triggered' and service_id"""
    filtered = []

    for incident in incidents:
        status = incident.get('status')
        service = incident.get('service', {})
        incident_service_id = service.get('id')

        if status == 'triggered' and incident_service_id == service_id:
            filtered.append(incident)

    return filtered

def resolve_incident(incident_id, api_key, user_email):
    """Send PUT request to resolve a single incident"""
    url = f"https://api.pagerduty.com/incidents/{incident_id}"

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Token token={api_key}',
        'Content-Type': 'application/json',
        'From': user_email
    }

    payload = {
        "incident": {
            "type": "incident_reference",
            "status": "resolved"
        }
    }

    try:
        data = json.dumps(payload).encode('utf-8')
        request = Request(url, data=data, headers=headers, method='PUT')

        with urlopen(request) as response:
            response.read()

        return True, None

    except HTTPError as e:
        error_msg = f"{e.code} {e.reason}"
        try:
            error_data = json.loads(e.read().decode('utf-8'))
            error_detail = error_data.get('error', {}).get('message', '')
            if error_detail:
                error_msg += f" - {error_detail}"
        except:
            pass
        return False, error_msg

    except URLError as e:
        return False, f"URL Error: {e.reason}"

    except Exception as e:
        return False, str(e)

def main():
    print("=== PagerDuty Incident Resolver ===\n")

    # Load configuration
    config = load_config()
    api_key = config['api_key']
    user_email = config['user_email']
    service_id = config['service_id']
    rate_limit_delay = config.get('rate_limit_delay', 0.5)

    # Fetch all incidents
    all_incidents = get_all_incidents(api_key)

    # Filter incidents
    print(f"Filtering incidents (status='triggered', service_id='{service_id}')...")
    filtered_incidents = filter_incidents(all_incidents, service_id)
    print(f"Found {len(filtered_incidents)} incidents matching criteria\n")

    if len(filtered_incidents) == 0:
        print("No incidents to resolve. Exiting.")
        return

    # Resolve incidents
    print("Resolving incidents...")
    successful = 0
    failed = []

    for i, incident in enumerate(filtered_incidents, 1):
        incident_id = incident['id']
        success, error = resolve_incident(incident_id, api_key, user_email)

        if success:
            successful += 1
        else:
            failed.append({
                'id': incident_id,
                'error': error
            })

        # Progress indicator
        print(f"Progress: {i}/{len(filtered_incidents)} incidents processed", end='\r')

        # Rate limiting
        if i < len(filtered_incidents):
            time.sleep(rate_limit_delay)

    print()  # New line after progress

    # Summary report
    print("\n=== Summary Report ===")
    print(f"Total incidents fetched: {len(all_incidents)}")
    print(f"Incidents matching criteria: {len(filtered_incidents)}")
    print(f"Successfully resolved: {successful}")
    print(f"Failed to resolve: {len(failed)}")

    if failed:
        print("\nFailed Incidents:")
        for item in failed:
            print(f"  - {item['id']}: {item['error']}")
    else:
        print("\nAll incidents resolved successfully!")

if __name__ == "__main__":
    main()
