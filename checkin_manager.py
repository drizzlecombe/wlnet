#!/usr/bin/env python

# -----------------------------------------------------------------------------
#
# A module for managing LOARES Winlink net check-ins
#
# Author: Andrew Watson
# 
# -----------------------------------------------------------------------------
import argparse
import csv
from checkins import add_checkin, get_last_checkin_repr
from storage import start_database, close_database,\
                    create_checkin_table, StorageException

CHECKIN_NUM_COLUMNS = 7 # TODO - set this value via a configuration file
CHECKIN_FIELD_NAMES = ('week_number', 
                       'callsign',
                       'transport_mode',
                       'rms_gateway',
                       'rms_frequency',
                       'location',
                       'state')
# ------------------------------------------------------------------------------
def process_command_line():
    parser = argparse.ArgumentParser(description='Clean a check-in CSV file.')
    parser.add_argument('-n',
                        '--nheaders',
                        type=int,
                        default=0,
                        help='The number of header lines to ignore. Default 0')

    # The file list is whatever we get as optional arguments at the end of the
    # command line. There must be one file name, however and nargs catches this
    # with the '+' symbol (at least one).
    parser.add_argument('file_list',
                        metavar='File',
                        type=str,
                        nargs='+', # Plus means at least one file name arg.
                        help='A list of file names to process')
    args = parser.parse_args()
    return (args.nheaders, args.file_list)
# -----------------------------------------------------------------------------

def scan_file(csv_file_name, num_header_lines):
    with open(csv_file_name, "r", newline='') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=CHECKIN_FIELD_NAMES)
        header_line_count = 0
        for checkin_line in reader:
            if header_line_count < num_header_lines:
                header_line_count += 1
                continue

            if len(checkin_line.keys()) != CHECKIN_NUM_COLUMNS:
                raise ValueError(f'Check-in has invalid num cols: {checkin_line}')
            clean_checkin_line = dict((k.strip(), v.strip()) for k, v in checkin_line.items())
            add_checkin(int(clean_checkin_line['week_number']),
                        clean_checkin_line['callsign'],
                        clean_checkin_line['transport_mode'],
                        clean_checkin_line['rms_gateway'],
                        float(clean_checkin_line['rms_frequency']),
                        clean_checkin_line['location'],
                        clean_checkin_line['state'])

            print(f'{get_last_checkin_repr()}')

# ------------------------------------------------------------------------------
def main():
    # Set up command line parsing
    (num_header_lines, csv_file_list) = process_command_line()

    start_database('basic_test.db')
    create_checkin_table()

    for csv_file_name in csv_file_list:
        scan_file(csv_file_name, num_header_lines)
    close_database()
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    main()

