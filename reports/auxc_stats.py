#!/usr/bin/env python

# -----------------------------------------------------------------------------
#
# Generates a CARES Winlink net participation report for operators.
#
# This tool uses the source .CSV file as input - not a database right now.
#
# Author: Andrew Watson
# 
# -----------------------------------------------------------------------------

import argparse
import csv

# NOTE: the following modules has to be in the PYTHONPATH For example, running
# from the root of this project: $ export PYTHONPATH=./src
import config
from validator import validate_checkins, Checkin


NET_START_WEEK = 105

# ------------------------------------------------------------------------------
def process_command_line():
    parser = argparse.ArgumentParser(description='Run an AUXC report.')
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
def remove_out_of_range_checkins(lowest_week_number, checkins):
    """Filters checkins keeping only those after but including a specific week number
     
    Returns a list of Checkin types  
     """
 
    in_range_checkins = []
    for checkin in checkins:
        week_number = int(checkin.week_number)
        if week_number >= lowest_week_number:
            in_range_checkins.append(checkin)
    return in_range_checkins

# -----------------------------------------------------------------------------

def checkins_by_callsign(checkins: Checkin):
    """Runs through all the checkins and arranges them by the operator's
    callsign
    
    Results in a dict, keyed by callsign. The value associated with a
    callsign is a list of checkins
    
    """
    checkins_by_callsign = {}
    for checkin in checkins:
        # Every AUXC is given a list to hold their checkins. Add any checkin for
        # that AUXC to their list.
        auxcs_checkins = checkins_by_callsign.setdefault(checkin.callsign, [])
        auxcs_checkins.append(checkin)
    return checkins_by_callsign

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

    config.load_config_file('config.json')
    raw_checkins_filename = config.get_raw_checkin_filename()
    raw_checkins_col_names = config.get_raw_checkin_fieldnames()
    checkins = load_csv_file(raw_checkins_filename, 1, raw_checkins_col_names)

    (valid_checkins, invalid_checkins) = validate_checkins(checkins)
    print(f'Total number of valid checkins for all weeks: {len(valid_checkins)}')

    required_checkins = remove_out_of_range_checkins(NET_START_WEEK, valid_checkins)
    print(f'Number of checkins after or including week {NET_START_WEEK}: {len(required_checkins)}')

    by_auxc = checkins_by_callsign(required_checkins)
    for auxc in by_auxc.keys():
        print(f'{auxc}, {len(by_auxc[auxc])}')

    """gen_report(checkins_by_callsign_then_week,
               DEFAULT_START_CHECKIN_DATE,
               DEFAULT_START_CHECKIN_WEEK,
               DEFAULT_END_CHECKIN_WEEK) """

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    main()

