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
from checkin import validate_checkins
import config
from storage import start_database, close_database,\
                    create_checkin_table, save_checkins, StorageException

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

def scan_file(csv_file_name: str, num_header_lines: int,
              column_names: list[str]) -> list[dict]:
    """Reads in the raw checkin contents from a CSV file
    
    Returns - all the rows in a dictionary. The keys are the column
    names from the file.
    """
    raw_checkins = []
    file_line_number = 0
    with open(csv_file_name, "r", newline='') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=column_names)

        header_line_count = 0
        for raw_checkin in reader:
            file_line_number += 1
            if header_line_count < num_header_lines:
                header_line_count += 1
                # We've read a header line - skip
                continue
            raw_checkin['line_number'] = file_line_number
            raw_checkins.append(raw_checkin)
    return raw_checkins

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



    raw_checkins = scan_file(raw_checkins_filename,
                             num_header_lines,
                             raw_checkins_col_names)
    (valid_checkins, invalid_checkins) = validate_checkins(raw_checkins)
    if len(invalid_checkins) == 0:
        try:
            start_database(database_name)
            create_checkin_table()
            save_checkins(valid_checkins)
            close_database()
        except StorageException as e:
            print(e)
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    main()

