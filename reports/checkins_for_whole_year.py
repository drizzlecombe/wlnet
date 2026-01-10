#!/usr/bin/env python
#
# Programme to list all check-ins for a given year.
#
from datetime import date, timedelta
import csv

BASE_DATE = date(2022, 11, 2)

year_of_interest = 2025

checkins_for_year = []
with open("../raw_data/all_checkins_loares_winlink_net.csv", "r", newline='') as csv_file:
    num_header_lines = 1
    reader = csv.reader(csv_file)
    header_line_count = 0
    for checkin_line in reader:
        if header_line_count < num_header_lines:
            header_line_count += 1
            continue
        week_number = int(checkin_line[0])
        week_offset = week_number - 1
        check_in_date = BASE_DATE + timedelta(weeks=week_offset)
        current_year = check_in_date.year

        if current_year == year_of_interest:
            callsign = checkin_line[1].strip().split('/')[0].upper()
            checkins_for_year.append((week_number, check_in_date, callsign))
# Get a list of unique check-ins. Sometimes we call these distinct check-ins.
# Only count one check-in per week per AUXC.
# The following uses dict.fromkeys rather than a set because fromkeys guarantees
# that the order is maintained in the list.
unique_checkins_for_year = list(dict.fromkeys(checkins_for_year))
for c in unique_checkins_for_year:
    week_number, checkin_date, callsign = c
    print(f"{week_number}, {checkin_date}, {callsign}")