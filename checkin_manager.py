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
import config
from storage import start_database, close_database,\
                    create_checkin_table, StorageException

# ------------------------------------------------------------------------------
def process_command_line():
    parser = argparse.ArgumentParser(description='Clean a check-in CSV file.')
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

def scan_file(csv_file_name: str, num_header_lines: int, col_names: list[str]) -> None:
    num_cols = len(col_names)
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
            clean_checkin_line = dict((k.strip(), v.strip()) \
                                      for k, v in checkin_line.items())
            
            add_checkin(int(clean_checkin_line[col_names[0]]),
                        clean_checkin_line[col_names[1]],
                        clean_checkin_line[col_names[2]],
                        clean_checkin_line[col_names[3]],
                        float(clean_checkin_line[col_names[4]]),
                        clean_checkin_line[col_names[5]],
                        clean_checkin_line[col_names[6]])
            
            print(f'{get_last_checkin_repr()}')

# -----------------------------------------------------------------------------
def main():
    # Set up command line parsing. Command line takes precedence over the
    # config file to allow quick experiments without having to change the
    # config.
    config.load_config_file('config.json')
    raw_checkins_filename = config.get_raw_checkin_filename()
    raw_checkins_col_names = config.get_raw_checkin_fieldnames()
    num_header_lines = config.get_num_header_lines()
    database_name = config.get_database_name()
    
    (cl_num_header_lines, cl_raw_checkins_filename) = process_command_line()

#   TODO: Need to check to see if config file values actually exist
    if cl_num_header_lines is not None:
        num_header_lines = cl_num_header_lines

    if cl_raw_checkins_filename is not None:
        raw_checkins_filename = cl_raw_checkins_filename

    start_database(database_name)
    create_checkin_table()

    scan_file(raw_checkins_filename, num_header_lines, raw_checkins_col_names)
    close_database()
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    main()

