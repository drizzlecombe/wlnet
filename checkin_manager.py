#!/usr/bin/env python

# -----------------------------------------------------------------------------
#
# A module for managing LOARES Winlink net check-ins
#
# Author: Andrew Watson
# 
# -----------------------------------------------------------------------------
import argparse
import sys
from checkins import add_checkin, get_last_checkin_repr

CHECKIN_NUM_COLUMNS = 7 # TODO - set this value via a configuration file

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
    with open(csv_file_name, "r") as csv:
        total_lines_processed = 0
        header_line_count = 0
        for line in csv:
            trimmed_line = line.rstrip('\n')
            if header_line_count < num_header_lines:
                header_line_count += 1
                continue

            raw_checkin = [col.strip() for col in trimmed_line.split(',')]

            if len(raw_checkin) != CHECKIN_NUM_COLUMNS:
                raise ValueError(f'Check-in has invalid num cols: {raw_checkin}')

            (week_num, 
             callsign,
             mode,
             rms,
             freq,
             location,
             state) = tuple(raw_checkin)
            
            add_checkin(int(week_num), callsign, mode, rms, \
                        float(freq), location, state)
            
            total_lines_processed += 1
            print(f'{total_lines_processed}, {get_last_checkin_repr()}')
        print(f'\n{csv_file_name}: total checkins processed '\
              f'- {total_lines_processed}')
        print()
        

# ------------------------------------------------------------------------------
def main():
    # Set up command line parsing
    (num_header_lines, csv_file_list) = process_command_line()

    for csv_file_name in csv_file_list:
        scan_file(csv_file_name, num_header_lines)

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    main()

