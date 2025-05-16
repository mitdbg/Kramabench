import requests
import os
import sys
from datetime import datetime
import json  # Import json library to parse response

# --- Configuration ---
# !!! WARNING: Hardcoding credentials is NOT recommended due to security risks !!!
SPACETRACK_USER = "lichenni@mit.edu"
SPACETRACK_PASSWORD = "elQ!4ITS!Ag!WPRv"  # <-- Very insecure!

# --- User Input: Modify these values ---
NORAD_CAT_ID = "25544"  # Example: ISS
TARGET_YEAR = 2023  # Year to filter for locally
REQUEST_FORMAT = "json"
# Start with a larger limit, remove 'limit' entirely later if needed for full history
DATA_LIMIT = 10000

OUTPUT_FILENAME = f"historical_data_{NORAD_CAT_ID}_limit{DATA_LIMIT}.{REQUEST_FORMAT}"
FILTERED_FILENAME = f"filtered_{TARGET_YEAR}_data_{NORAD_CAT_ID}.{REQUEST_FORMAT}"

# --- API Details ---
BASE_URL = "https://www.space-track.org"
LOGIN_URL = f"{BASE_URL}/ajaxauth/login"
QUERY_ENDPOINT = f"{BASE_URL}/basicspacedata/query/class/gp_history"


# --- Script Logic ---
def get_and_filter_historical_data():
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    )

    try:
        # 1. Login
        login_data = {"identity": SPACETRACK_USER, "password": SPACETRACK_PASSWORD}
        print(f"Attempting session login...")
        resp_login = session.post(LOGIN_URL, data=login_data)
        resp_login.raise_for_status()
        content_type = resp_login.headers.get("Content-Type", "").lower()
        if "html" in content_type:
            print("Login likely failed: Received HTML.", file=sys.stderr)
            sys.exit(1)
        print("Login successful.")

        # 2. Fetch Data (Simplified Query with Limit)
        print(f"\nQuerying Space-Track for historical data...")
        query_params = {
            "norad_cat_id": NORAD_CAT_ID,
            "format": REQUEST_FORMAT,
            "limit": DATA_LIMIT,  # Fetching more records now
            # No EPOCH filter, no orderby
        }
        print(f"Endpoint: {QUERY_ENDPOINT}")
        print(f"Parameters: {query_params}")

        resp_query = session.get(QUERY_ENDPOINT, params=query_params)
        resp_query.raise_for_status()
        print("Data query request successful.")

        if not resp_query.text or resp_query.text.strip() == "[]":
            print(f"No historical data found for NORAD ID {NORAD_CAT_ID}.")
            return

        print(
            f"Historical data received (Format: {REQUEST_FORMAT}, Limit: {DATA_LIMIT})."
        )

        # Save the raw downloaded data (optional but good for reference)
        try:
            with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
                f.write(resp_query.text)
            print(f"Raw data saved to {OUTPUT_FILENAME}")
        except IOError as e:
            print(
                f"Error writing raw data to file {OUTPUT_FILENAME}: {e}",
                file=sys.stderr,
            )

        # 3. Filter Data Locally
        print(f"\nFiltering data for EPOCH year {TARGET_YEAR}...")
        try:
            all_data = json.loads(resp_query.text)  # Parse the JSON response
            filtered_data = []
            count = 0
            for record in all_data:
                # Check if EPOCH field exists and starts with the target year
                if "EPOCH" in record and record["EPOCH"].startswith(str(TARGET_YEAR)):
                    filtered_data.append(record)
                    count += 1

            print(f"Found {count} records with EPOCH in {TARGET_YEAR}.")

            if filtered_data:
                # Save the filtered data
                try:
                    with open(FILTERED_FILENAME, "w", encoding="utf-8") as f:
                        json.dump(
                            filtered_data, f, indent=4
                        )  # Save filtered JSON prettily
                    print(
                        f"Filtered data for {TARGET_YEAR} saved to {FILTERED_FILENAME}"
                    )
                except IOError as e:
                    print(
                        f"Error writing filtered data to file {FILTERED_FILENAME}: {e}",
                        file=sys.stderr,
                    )
            else:
                print(
                    f"No records found matching the target year {TARGET_YEAR} within the downloaded data (limit {DATA_LIMIT}). You might need to increase the limit or remove it to fetch the full history."
                )

        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse JSON response: {e}", file=sys.stderr)
            print("Check the raw output file to see the response content.")

    except requests.exceptions.Timeout as e:
        print(f"Error: Request timed out: {e}", file=sys.stderr)
    except requests.exceptions.HTTPError as e:
        print(
            f"Error: HTTP Error: {e.response.status_code} {e.response.reason}",
            file=sys.stderr,
        )
        print(f"Response text: {e.response.text}", file=sys.stderr)
    except requests.exceptions.RequestException as e:
        print(f"Error: A network request error occurred: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
    finally:
        session.close()
        print("Session closed.")


# --- Execute the function ---
if __name__ == "__main__":
    get_and_filter_historical_data()
