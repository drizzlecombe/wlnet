#!/usr/bin/env python
#
# Programme to list all check-ins for a given year.
#
import argparse
import csv
from datetime import date, timedelta
import sys

BASE_DATE = date(2022, 11, 2)

# -----------------------------------------------------------------------------
def validate_year(year_number: int) -> int:
    year_today = date.today().year
    if year_number < BASE_DATE.year or year_number > year_today:
        print(f"Error: {sys.argv[0]}: "
              f"Year value is out of range: {BASE_DATE.year} < {year_number} <= {year_today}")
        sys.exit(2)
    return year_number

# -----------------------------------------------------------------------------
def process_command_line() -> tuple[int, str]:
    parser = argparse.ArgumentParser()

    # Positional arguments - these MUST be specified on the command line.
    parser.add_argument("year", help="The year that checkins are needed for.", type=int)
    parser.add_argument("file_name", help="The file where the CSV data is stored.")
    args = parser.parse_args()
    requested_year = validate_year(args.year)
    file_name = args.file_name
    return (requested_year, file_name)

# -----------------------------------------------------------------------------
def load_csv_data(filename: str, year_requested: int=2025) -> list[tuple[int, date, str]]:
    checkins_for_year = []
    with open(filename, "r", newline='') as csv_file:
        num_header_lines = 1
        reader = csv.reader(csv_file)
        header_line_count = 0
        for checkin_line in reader:
            if header_line_count < num_header_lines:
                header_line_count += 1
                continue
            week_number = int(checkin_line[0])

            # The Winlink net started on week 1 rather than week 0. So, to find out
            # how many weeks have elapsed between the net's start date (week 1, on
            # BASE_DATE) we have to subtract one from the week number.
            #
            # For example: how many weeks between week 3 and week 1?
            # Answer: 2 = later week number, 3 - 1.
            week_offset = week_number - 1
            check_in_date = BASE_DATE + timedelta(weeks=week_offset)

            if check_in_date.year == year_requested:
                callsign = checkin_line[1].strip().split('/')[0].upper()
                checkins_for_year.append((week_number, check_in_date, callsign))
    return checkins_for_year

# -----------------------------------------------------------------------------
def get_unique_checkins(checkins: list[tuple[int, date, str]]) \
                                -> list[tuple[int, date, str]]:
    # Get a list of unique check-ins. Sometimes we call these distinct check-ins.
    # Only count one check-in per week per AUXC.
    # The following uses dict.fromkeys rather than a set because fromkeys guarantees
    # that the order is maintained in the list.
    unique_checkins = list(dict.fromkeys(checkins))
    return unique_checkins

# -----------------------------------------------------------------------------
def all_unique_checkins_report(checkins: list[tuple[int, date, str]]) -> None:
    for c in checkins:
        week_number, checkin_date, callsign = c
        print(f"{week_number}, {checkin_date}, {callsign}")

# -----------------------------------------------------------------------------
def unique_checkin_counts_by_callsign(checkins: list[tuple[int, date, str]]) -> None:
    cs_counts = {}
    for c in checkins:
        week_number, checkin_date, callsign = c
        count_for_callsign = cs_counts.setdefault(callsign, 0)
        cs_counts[callsign] = count_for_callsign + 1

    # If two callsigns share a count, arrange those callsigns in lexicographical
    # order. Since Python sorting is stable, we can take advantage of this by
    # sorting by callsign first, then by counts. Any callsigns that have equal
    # counts will retain their order from the first sort - lexicographically.
    ordered_by_callsign = sorted(list(cs_counts.items()), key=lambda x: x[0], reverse=False) 
    ordered_by_counts = sorted(ordered_by_callsign, key=lambda x: x[1], reverse=True)
    for oc in ordered_by_counts:
        callsign, count = oc
        print(f"{callsign}, {count}")
# -----------------------------------------------------------------------------
# Programme entry point
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    year, filename = process_command_line()
    checkins_requested = load_csv_data(filename, year)
    unique_checkins = get_unique_checkins(checkins_requested)
    all_unique_checkins_report(unique_checkins)
    unique_checkin_counts_by_callsign(unique_checkins)