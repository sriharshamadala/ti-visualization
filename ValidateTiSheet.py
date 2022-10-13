"""
This script validates the ti-sheet json file. It prints entries that need to be manually fixed.

Currently we look at the following issues:
    Entries that don't have an end time
    Entries that span more than 3 days (more than a weekend)
"""

import sys
import json 
from datetime import datetime, timedelta

max_continous_days = 3

if __name__ == '__main__':
    time_tracker_file = open(sys.argv[1])
    time_tracker_str = time_tracker_file.read()
    time_tracker_data = json.loads(time_tracker_str)["work"]

    for time_entry in time_tracker_data:
        time_entry['start'] = datetime.strptime(
                time_entry['start'],
                "%Y-%m-%dT%H:%M:%S.%fZ")
        if ('end' in time_entry):
            time_entry['end'] = datetime.strptime(
                    time_entry['end'],
                    "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            # If missing end, this entry needs validation
            print("Validate this entry:")
            print(time_entry['name'])
            print(time_entry['start'])
            print("===============================")
            continue

        if (time_entry['end'] - time_entry['start']).days >= max_continous_days:
            print("Validate this entry:")
            print(time_entry['name'])
            print(time_entry['start'])
            print(time_entry['end'])
            print("===============================")

