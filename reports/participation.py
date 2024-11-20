#!/usr/bin/env python

# -----------------------------------------------------------------------------
#
# Generates a Winlink net participation report for operators
#
# Author: Andrew Watson
# 
# -----------------------------------------------------------------------------
import argparse
from collections import defaultdict
import csv
import datetime

import config


DEFAULT_START_CHECKIN_WEEK = 61 # First week of period of interest
DEFAULT_END_CHECKIN_WEEK   = 104 # Last week of second year

DEFAULT_START_CHECKIN_DATE = datetime.date(2024, 1, 2)

# ------------------------------------------------------------------------------
def process_command_line():
    parser = argparse.ArgumentParser(description='Run a participation report.')
    parser.add_argument('-n',
                        '--nheaders',
                        type=int,
                        default=None,
                        help='The number of header lines to ignore. Default 0')

    # The file list is whatever we get as optional arguments at the end of the
    # command line. There must be one file name, however and nargs catches this
    # with the '+' symbol (at least one).
    parser.add_argument('-f',
                        '--raw_checkins_filename',
                        metavar='File',
                        type=str,
                        default=None,
                        help='The name of the raw checkins file to process')
    args = parser.parse_args()
    return (args.nheaders, args.raw_checkins_filename)
# -----------------------------------------------------------------------------

def load_csv_file(csv_file_name: str, num_header_lines: int, col_names: list[str]) -> None:
    num_cols = len(col_names)
    raw_checkins = []
    with open(csv_file_name, "r", newline='') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=col_names)
        header_line_count = 0
        for checkin_line in reader:
            if header_line_count < num_header_lines:
                header_line_count += 1
                continue

            if len(checkin_line.keys()) != num_cols:
                raise ValueError('Check-in has invalid num cols: '
                                 f'{checkin_line}')
            raw_checkins.append(checkin_line)
    return raw_checkins
# -----------------------------------------------------------------------------
def remove_out_of_range_checkins(low_threshold_week_number,
                                 high_threshold_week_number,
                                   checkins):
    """Filters checkins keeping only those in the closed range given by
    the thresholds """
    assert low_threshold_week_number < high_threshold_week_number, "Thresholds reversed"
    required_checkins = []
    for checkin in checkins:
        week_number = int(checkin['week_number'])
        if week_number >= low_threshold_week_number and \
            week_number <= high_threshold_week_number:
            required_checkins.append(checkin)
    return required_checkins

# -----------------------------------------------------------------------------

def group_by_callsign(checkins, end_week):
    """Runs through all the checkins and arranges them by the operator's
    callsign
    
    Results in a dict, keyed by callsign. The value associated with a
    callsign is a list. Each cell contains a count of checkins for that
    week.
    
    """
    # Each callsign has a list of zeros that ranges between index 0 and
    # the index that equals the last specified check-in week. If a
    # check-in happens for week n, then the nth cell of this list is incremented.
    by_callsign = defaultdict(lambda: [0] * (end_week + 1))
    for checkin in checkins:
        # There may be mobile operations. Strip any '/M' or other
        # suffixes from the callsigns.
        callsign = checkin['callsign'].split('/')[0].strip()
        by_callsign[callsign][int(checkin['week_number'])] += 1
    return by_callsign

# -----------------------------------------------------------------------------
def gen_week_number_to_checkin_date(start_date, start_week, end_week):
    """Creates a LUT that converts from a net week number to an actual
    date
    
    The date used is the deadline for the check-in.
    """
    week_to_date_LUT = {}
    week_count = 0
    for week_number in range(start_week, end_week + 1):
        checkin_date = start_date + datetime.timedelta(weeks=week_count)
        week_to_date_LUT[week_number] = checkin_date.isoformat()
        week_count += 1
    return week_to_date_LUT

# -----------------------------------------------------------------------------

def gen_report(checkins_by_callsign_then_week, start_date, start_week, end_week):

    w2dLUT = gen_week_number_to_checkin_date(start_date, start_week, end_week)
    # print header
    header = 'Callsign, '
    for week in range(start_week, end_week + 1):
        header += f'"{w2dLUT[week]}", '
    print(header)

    # Now print out a checkin status for each callsign for each week.
    callsigns = checkins_by_callsign_then_week.keys()
    for callsign in sorted(callsigns):
        line = f'{callsign}, '
        for num in checkins_by_callsign_then_week[callsign][start_week:]:
            checked_in_this_week = 'FALSE, '
            if num > 0:
                checked_in_this_week = 'TRUE, '
            line += checked_in_this_week
        print(line)
# -----------------------------------------------------------------------------
def main():
    # Set up command line parsing.
    # Not implemented - use this one day to generate more date-flexible reports
    # (cl_num_header_lines, cl_raw_checkins_filename) = process_command_line()
    #
    # NOTE: the config module has to be in the PYTHONPATH
    # For example, running from the root of this project:
    #  $ export PYTHONPATH=./src
    config.load_config_file('config.json')
    raw_checkins_filename = config.get_raw_checkin_filename()
    raw_checkins_col_names = config.get_raw_checkin_fieldnames()
    checkins = load_csv_file(raw_checkins_filename, 1, raw_checkins_col_names)
    print(f'Number of checkins: {len(checkins)}')
    required_checkins = remove_out_of_range_checkins(DEFAULT_START_CHECKIN_WEEK,
                                                     DEFAULT_END_CHECKIN_WEEK,
                                                     checkins)
    print(f'Number of checkins after or including week {DEFAULT_START_CHECKIN_WEEK}: {len(required_checkins)}')
    checkins_by_callsign_then_week = group_by_callsign(required_checkins, DEFAULT_END_CHECKIN_WEEK)
    gen_report(checkins_by_callsign_then_week,
               DEFAULT_START_CHECKIN_DATE,
               DEFAULT_START_CHECKIN_WEEK,
               DEFAULT_END_CHECKIN_WEEK)
        



# -----------------------------------------------------------------------------

if __name__ == '__main__':
    main()

