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
from checkin import validate_checkins, Checkin

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

def load_csv_file(csv_file_name: str, num_header_lines: int,
                  col_names: list[str], threshold_week: int = 1) -> None:
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
            
            # Ignore checkins for week numbers before our threshold
            if int(checkin_line['week_number']) >= threshold_week:
                raw_checkins.append(checkin_line)
    return raw_checkins

# -----------------------------------------------------------------------------
class Auxc:
    # This is the set of Assistant Emergency Coordinators' callsigns
    aec_set = None

    def __init__(self, callsign):
        self.callsign = callsign
        self.is_AEC = False
        if Auxc.aec_set is not None:
            self.is_AEC = self.callsign in Auxc.aec_set
        self.distinct_checkin_cnt = 0
        self.checkin_rf_cnt = 0
        self.checkin_not_rf_cnt = 0
        self.distinct_checkin_weeks = set()

    def add_checkin(self, checkin):
        if not isinstance(checkin, Checkin):
            raise TypeError(f"Not an instance of Checkin: {checkin}")

        # TODO: Put the non-RF mode values in the configuration file.
        if checkin.transport_mode in ['TELNET', 'WEBMAIL', 'SMTP']:
            self.checkin_not_rf_cnt += 1
        else:
            self.checkin_rf_cnt += 1

        # Only one check-in is considered per week. If multiple check-ins happen
        # during a week, they are just treated as one.
        self.distinct_checkin_weeks.add(checkin.week_number)

    def num_distinct_checkins(self):
        return len(self.distinct_checkin_weeks)
    
    def __lt__(self, other):
        """AUXCs are sortable. They are ranked by the number of distinct
        checkins. More distinct checkins means an earier position in the overall
        list of AUXCs. If two or more AUXCs have the same number of distinct
        checkins, then they are sorted by callsign lexicographically."""

        if not isinstance(other, Auxc):
            raise TypeError(f'{self.callsign}: '\
                            'The other value is not an instance of Auxc')
        
        if self.num_distinct_checkins() == other.num_distinct_checkins():
            # Same number of distinct checkins, so order lexicographically.
            return self.callsign > other.callsign
        return self.num_distinct_checkins() < other.num_distinct_checkins()
     
    def __repr__(self):
        # {self.checkin_rf_cnt}, '\
        # f'{self.checkin_not_rf_cnt}, '\
        # f'{self.checkin_rf_cnt + self.checkin_not_rf_cnt}, '\

        aec_indicator = ''
        if self.is_AEC:
            aec_indicator = 'Y'
        return f'{self.callsign}, {aec_indicator}, {self.num_distinct_checkins()}'

    def __str__(self):
        return self.__repr__()
# -----------------------------------------------------------------------------

def checkins_by_callsign(checkins: list[Checkin]):
    """Runs through all the checkins and arranges them by the operator's
    callsign
    
    Results in a dict, keyed by callsign. The value associated with a
    callsign is a list of checkins
    
    """
    auxcs = {}
    for checkin in checkins:
        # Every AUXC is given a list to hold their checkins. Add any checkin for
        # that AUXC to their list.
        auxc = auxcs.setdefault(checkin.callsign, Auxc(checkin.callsign))
        auxc.add_checkin(checkin)
    return auxcs

# -----------------------------------------------------------------------------
def main():
    # Set up command line parsing.
    # Not implemented - use this one day to generate more date-flexible reports
    # (cl_num_header_lines, cl_raw_checkins_filename) = process_command_line()

    config.load_config_file('config.json')
    raw_checkins_filename = config.get_raw_checkin_filename()
    raw_checkins_col_names = config.get_raw_checkin_fieldnames()
    Auxc.aec_set = config.get_aecs()
    CARES_net_start_week_num = config.get_start_week_num()

    checkins = load_csv_file(raw_checkins_filename, 1,
                             raw_checkins_col_names,
                             CARES_net_start_week_num)

    (valid_checkins, invalid_checkins) = validate_checkins(checkins)
    print(f'Number of checkins after or including week '
          f'{CARES_net_start_week_num}: {len(valid_checkins)}')

    print('The net has been running '
          f'{Checkin.max_week_number - CARES_net_start_week_num + 1} '
          'weeks')
    auxcs = checkins_by_callsign(valid_checkins)
    for auxc in sorted(auxcs.values(), reverse=True):
        print(auxc)

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    main()