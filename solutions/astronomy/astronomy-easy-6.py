#!/usr/bin/env python
# coding: utf-8
"""
Analyzes Starlink altitude decay rates using local CSV files from Space-Track.

Compares decay during a quiet period (May 1-4, 2024) vs. a storm period
(May 10-13, 2024) based on GP History data.

Requires CSV files containing GP History data in the same directory as the script, named according to the 'file_mapping' dictionary below.
"""

import csv
import math
from datetime import datetime, timezone, timedelta
import os # To handle file paths
import sys # For error output

# === Constants ===
MU_EARTH = 398600.4418  # km^3/s^2 (Standard gravitational parameter for Earth)
SECONDS_PER_DAY = 86400.0

# === Helper Functions ===

def calculate_semi_major_from_mean_motion(mean_motion_rev_per_day):
    """Calculates mean altitude based on TLE mean motion (revs/day)."""
    if mean_motion_rev_per_day is None:
        return None
        
    mean_motion_rev_per_day = float(mean_motion_rev_per_day)
    if mean_motion_rev_per_day <= 0:
        return None

    mean_motion_rad_per_sec = mean_motion_rev_per_day * 2.0 * math.pi / SECONDS_PER_DAY
    # Calculate semi-major axis using Kepler's Third Law: a = (mu / n^2)^(1/3)
    semi_major_axis_km = (MU_EARTH / (mean_motion_rad_per_sec ** 2)) ** (1.0 / 3.0)
    return semi_major_axis_km

def parse_epoch(epoch_str):
    """Parses Space-Track EPOCH string into a timezone-aware datetime object."""
    # Handle formats like "YYYY-MM-DD HH:MM:SS.ffffff" or "YYYY-MM-DDTHH:MM:SS.ffffff"
    epoch_str_cleaned = epoch_str.replace(' ', 'T')
    # Ensure there's fractional seconds part for strptime robustness if needed
    if '.' not in epoch_str_cleaned:
         epoch_str_cleaned += '.0'
    # Try parsing with microseconds
    dt_obj = datetime.strptime(epoch_str_cleaned, '%Y-%m-%dT%H:%M:%S.%f')

    # Assume UTC (Space-Track standard)
    return dt_obj.replace(tzinfo=timezone.utc)


def find_relevant_records_from_list(gp_records_list, analysis_start_dt, analysis_end_dt):
    """
    Finds the earliest record >= start_dt and latest record <= end_dt from a list
    of GP records (dictionaries read from CSV).
    Assumes the list might not be sorted initially.
    """
    if not gp_records_list:
        return None, None

    # Parse epochs and filter out records where epoch can't be parsed
    parsed_records = []
    for record in gp_records_list:
        epoch_dt = parse_epoch(record.get("EPOCH"))
        if epoch_dt:
            parsed_records.append({"epoch_dt": epoch_dt, "record": record})
        else:
            print(f"  Warning: Skipping record due to unparseable epoch: {record.get('EPOCH')}", file=sys.stderr)

    if not parsed_records:
        return None, None

    # Sort records by parsed epoch time
    parsed_records.sort(key=lambda r: r["epoch_dt"])

    first_record_data = None
    last_record_data = None

    # Find the first record within or just before the analysis start window
    potential_first = None
    for item in parsed_records:
        if item["epoch_dt"] >= analysis_start_dt:
            first_record_data = item["record"]
            break # Found the first one at or after the start
        potential_first = item["record"] # Keep track of latest before start

    if first_record_data is None:
        first_record_data = potential_first # Use the one just before if none are after start

    # Find the last record within the analysis end window
    potential_last = None
    for item in reversed(parsed_records): # Search backwards for efficiency
         if item["epoch_dt"] <= analysis_end_dt:
              # Ensure this record is not before the chosen first record's epoch
              if first_record_data:
                   first_epoch_dt = parse_epoch(first_record_data.get("EPOCH"))
                   if first_epoch_dt and item["epoch_dt"] >= first_epoch_dt:
                        last_record_data = item["record"]
                        break # Found the last one at or before the end, and after the start
              else: # Should not happen if potential_first logic worked, but as safety
                   last_record_data = item["record"]
                   break
         # Keep track of the earliest record after the end window as a fallback? No, usually want latest *within*.

    # If no record found within end window, but we have a start record
    if last_record_data is None and first_record_data is not None:
         # Check if the very last record overall is usable (i.e. same or after first record)
         last_available_epoch = parsed_records[-1]["epoch_dt"]
         first_epoch_dt = parse_epoch(first_record_data.get("EPOCH"))
         if first_epoch_dt and last_available_epoch >= first_epoch_dt:
              last_record_data = parsed_records[-1]["record"]
              # print("  Info: Using last available record as end point as none were strictly within end boundary.")


    # Final check: Ensure we have both and they are not the same record if possible
    if first_record_data and last_record_data:
        # Avoid using the exact same record if multiple exist
        if first_record_data.get("GP_ID") == last_record_data.get("GP_ID") and len(parsed_records) > 1:
             # This check might be too simplistic if GP_IDs repeat; rely on epoch instead
             first_epoch = parse_epoch(first_record_data.get("EPOCH"))
             last_epoch = parse_epoch(last_record_data.get("EPOCH"))
             if first_epoch == last_epoch and len(parsed_records) > 1:
                  print("  Warning: Start and end records are identical, cannot calculate rate.", file=sys.stderr)
                  return None, None # Cannot calculate rate with identical points

        # Check if first is actually before last
        first_epoch = parse_epoch(first_record_data.get("EPOCH"))
        last_epoch = parse_epoch(last_record_data.get("EPOCH"))
        if not first_epoch or not last_epoch or first_epoch > last_epoch:
             print("  Warning: Could not determine valid start/end epoch order.", file=sys.stderr)
             return None, None # Invalid state
    elif not first_record_data or not last_record_data:
         # If either is still None here, we don't have a valid pair
         return None, None


    return first_record_data, last_record_data


def calculate_decay_rate(start_record, end_record):
    """
    Calculates the average altitude decay rate between two GP records (dictionaries).
    Returns rate in km/day or None if calculation isn't possible.
    """

    start_epoch_str = start_record.get("EPOCH")
    start_mean_motion = start_record.get("MEAN_MOTION")
    end_epoch_str = end_record.get("EPOCH")
    end_mean_motion = end_record.get("MEAN_MOTION")


    start_mean_motion_f = float(start_mean_motion)
    end_mean_motion_f = float(end_mean_motion)

    # Calculate altitudes
    start_alt = calculate_semi_major_from_mean_motion(start_mean_motion_f)
    end_alt = calculate_semi_major_from_mean_motion(end_mean_motion_f)
    print(f"start alt:{start_alt}, end alt:{end_alt}")

    if start_alt is None or end_alt is None:
         print("  Calculation Error: Could not calculate altitude from mean motion.", file=sys.stderr)
         return None

    # Calculate time difference
    start_time = parse_epoch(start_epoch_str)
    end_time = parse_epoch(end_epoch_str)

    if not start_time or not end_time:
        print("  Calculation Error: Could not parse epoch strings.", file=sys.stderr)
        return None

    time_delta_seconds = (end_time - start_time).total_seconds()
    time_delta_days = time_delta_seconds / SECONDS_PER_DAY

    # Calculate altitude change
    altitude_delta_km = end_alt - start_alt # Will be negative for decay

    # Calculate rate
    decay_rate_km_per_day = altitude_delta_km / time_delta_days
    return decay_rate_km_per_day


# === Main Analysis Logic ===


# Define where your downloaded files are relative to the script location
# Assumes files are in the same directory as the script.
data_directory = "./data/astronomy/input/space-track/"

# Define the mapping between satellite IDs, periods, and filenames
# Uses the specific filenames identified from user uploads.
# Excludes satellites where data files were empty or not provided.
file_mapping = {
    "58214": {
        "quiet": "58214_quiet.csv",
        "storm": "58214_storm.csv"
    },

}
analyzed_ids = list(file_mapping.keys())
print(f"Analyzing data for NORAD IDs: {', '.join(analyzed_ids)}")

# Define analysis windows (UTC)
ANALYSIS_QUIET_START = datetime(2024, 5, 1, 0, 0, 0, tzinfo=timezone.utc)
ANALYSIS_QUIET_END = datetime(2024, 5, 4, 23, 59, 59, 999999, tzinfo=timezone.utc)
ANALYSIS_STORM_START = datetime(2024, 5, 10, 0, 0, 0, tzinfo=timezone.utc)
ANALYSIS_STORM_END = datetime(2024, 5, 13, 23, 59, 59, 999999, tzinfo=timezone.utc)

results = {} # Dictionary to store calculated rates {norad_id: {period: rate}}

# --- Loop through satellites and periods ---
for norad_id, period_files in file_mapping.items():
    print(f"\n--- Processing NORAD ID: {norad_id} ---")
    results[norad_id] = {"quiet_rate_km_day": None, "storm_rate_km_day": None}

    # --- Process Quiet Period File ---
    quiet_filename = period_files.get("quiet")
    if quiet_filename:
        filepath = os.path.join(data_directory, quiet_filename)
        print(f"  Reading Quiet File: {filepath}")

        quiet_records = []
        with open(filepath, 'r', encoding='utf-8', newline='') as f:
            # Check for empty file / only header
            first_line = f.readline()
            if not first_line:
                    print("  Warning: Quiet file appears empty.")
                    continue # Skip to next period/satellite

            # Check for "NO RESULTS RETURNED"
            if "NO RESULTS RETURNED" in first_line:
                    print("  Warning: Quiet file contains 'NO RESULTS RETURNED'.")
                    continue

            f.seek(0) # Rewind to read header with DictReader
            reader = csv.DictReader(f)
            # Check if header exists
            if not reader.fieldnames:
                    print(f"  Error: Could not read header from quiet file: {filepath}", file=sys.stderr)
                    continue

            # Check for required columns
            required_cols = ["EPOCH", "MEAN_MOTION"]
            if not all(col in reader.fieldnames for col in required_cols):
                print(f"  Error: Missing required columns ({', '.join(required_cols)}) in quiet file: {filepath}", file=sys.stderr)
                continue

            # Read data rows
            for row in reader:
                # Basic validation: ensure required fields are not empty strings
                if row.get("EPOCH") and row.get("MEAN_MOTION"):
                        quiet_records.append(row)
                else:
                        print(f"  Warning: Skipping row with missing required data in quiet file: {row}", file=sys.stderr)


        if quiet_records:
            print(f"    Read {len(quiet_records)} valid records.")
            q_start_rec, q_end_rec = find_relevant_records_from_list(
                quiet_records, ANALYSIS_QUIET_START, ANALYSIS_QUIET_END
            )
            if q_start_rec and q_end_rec:
                print(f"    Quiet period analysis window: {q_start_rec.get('EPOCH')} -> {q_end_rec.get('EPOCH')}")
                quiet_rate = calculate_decay_rate(q_start_rec, q_end_rec)
                results[norad_id]["quiet_rate_km_day"] = quiet_rate
                if quiet_rate is None:
                        print("    Failed to calculate quiet decay rate.")
            else:
                print("    Could not find suitable start/end records within the quiet analysis window.")
        else:
            print("    No valid records found in quiet file after reading.")



    # --- Process Storm Period File (Similar logic) ---
    storm_filename = period_files.get("storm")
    if storm_filename:
        filepath = os.path.join(data_directory, storm_filename)
        print(f"  Reading Storm File: {filepath}")

        storm_records = []
        with open(filepath, 'r', encoding='utf-8', newline='') as f:
                # Check for empty file / only header
            first_line = f.readline()
            if not first_line:
                    print("  Warning: Storm file appears empty.")
                    continue # Skip to next satellite

            # Check for "NO RESULTS RETURNED"
            if "NO RESULTS RETURNED" in first_line:
                    print("  Warning: Storm file contains 'NO RESULTS RETURNED'.")
                    continue

            f.seek(0) # Rewind to read header with DictReader
            reader = csv.DictReader(f)
                # Check if header exists
            if not reader.fieldnames:
                    print(f"  Error: Could not read header from storm file: {filepath}", file=sys.stderr)
                    continue

            # Check for required columns
            required_cols = ["EPOCH", "MEAN_MOTION"]
            if not all(col in reader.fieldnames for col in required_cols):
                print(f"  Error: Missing required columns ({', '.join(required_cols)}) in storm file: {filepath}", file=sys.stderr)
                continue

            # Read data rows
            for row in reader:
                    if row.get("EPOCH") and row.get("MEAN_MOTION"):
                        storm_records.append(row)
                    else:
                        print(f"  Warning: Skipping row with missing required data in storm file: {row}", file=sys.stderr)


        if storm_records:
            print(f"    Read {len(storm_records)} valid records.")
            s_start_rec, s_end_rec = find_relevant_records_from_list(
                storm_records, ANALYSIS_STORM_START, ANALYSIS_STORM_END
            )
            if s_start_rec and s_end_rec:
                print(f"    Storm period analysis window: {s_start_rec.get('EPOCH')} -> {s_end_rec.get('EPOCH')}")
                storm_rate = calculate_decay_rate(s_start_rec, s_end_rec)
                results[norad_id]["storm_rate_km_day"] = storm_rate
                if storm_rate is None:
                        print("    Failed to calculate storm decay rate.")
            else:
                print("    Could not find suitable start/end records within the storm analysis window.")
        else:
            print("    No valid records found in storm file after reading.")


    # --- Print individual results after processing both periods ---
    qr = results[norad_id].get('quiet_rate_km_day')
    sr = results[norad_id].get('storm_rate_km_day')
    print(f"  Result - Quiet Rate: {qr:.4f} km/day" if qr is not None else "  Result - Quiet Rate: Error/Unavailable")
    print(f"  Result - Storm Rate: {sr:.4f} km/day" if sr is not None else "  Result - Storm Rate: Error/Unavailable")



