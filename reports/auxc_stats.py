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
# Constants
# ------------------------------------------------------------------------------
NO_CHECKIN = 0
RF_CHECKIN = 1
NON_RF_CHECKIN = 2

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

    # The current week number for the net
    current_week_number = 0

    # The CARES net has been running this many weeks
    net_running_weeks = None

    # -------------------------------------------------------------------------
    def __init__(self, callsign):
        self.callsign = callsign.callsign
        self.is_AEC = False
        if Auxc.aec_set is not None:
            self.is_AEC = self.callsign in Auxc.aec_set

        # Assume that this AUXC has made no checkins yet.    
        self.distinct_checkin_cnt = 0

        # Only one check-in per week is counted. This is called a distinct
        # check-in. However, we keep the transport mode of each check-in to see
        # if any week has exclusively a non-RF distinct check-in. This
        # dictionary is keyed by distinct check-in week.
        self.distinct_checkin_type = {}

        # This is the proportion of the number of check-ins from the AUXC's
        # first check-in compared with the actual number of potential check-ins
        # from that first check-in. How many did he do compared to how many he
        # could've done.
        self.participation = 0.0

        # This is the first recorded week that the AUXC checked in.
        self.first_checkin_week = Auxc.current_week_number

        # The distinct gateways (RMSs) the AUXC checked-in through. This
        # differentiates by SSID. For example, KD7ZDO-11 and KD7ZDO-12 are
        # considered distinct gateways.
        self.distinct_gateways = set()

        # How many times has this AUXC checked in using Starlink
        self.used_starlink = 0

    # -------------------------------------------------------------------------
    def add_checkin(self, checkin):
        if not isinstance(checkin, Checkin):
            raise TypeError(f"Not an instance of Checkin: {checkin}")

        # Keep track of whether or not an RF checkin was used during a given
        # week for this AUXC
        week_checkin_type = self.distinct_checkin_type.setdefault(
            checkin.week_number,
            NO_CHECKIN)
        
        # TODO: Put the non-RF mode values in the configuration file.
        # TODO: This logic should shift to the Checkin class.
        if checkin.transport_mode in ['TELNET', 'WEBMAIL', 'SMTP']:
            # Don't update the distinct checkin type for this week if it is
            # already an RF_CHECKIN type. Only upgrade a NO_CHECKIN.
            if self.distinct_checkin_type[checkin.week_number] == NO_CHECKIN:
                # TODO: need to also check that the AUXC used the /M modifier
                # (even though lack of this forces an exception in the Checkin class)
                if checkin.transport_mode == 'TELNET' and checkin.gateway == 'STARLINK':
                    self.distinct_checkin_type[checkin.week_number] = RF_CHECKIN
                    self.used_starlink += 1
                else:
                    self.distinct_checkin_type[checkin.week_number] = NON_RF_CHECKIN
        else:
            # Since we have an RF_CHECKIN - these trump all other types. No need
            # to check what we have already set - just force this type.
            self.distinct_checkin_type[checkin.week_number] = RF_CHECKIN

        if checkin.gateway not in ['N/A', 'STARLINK']:
            self.distinct_gateways.add(checkin.gateway)

        # Participation is monitored from the first week that the AUXC checked
        # into the net.
        # TODO: account for hiatus.
        if checkin.week_number < self.first_checkin_week:
            self.first_checkin_week = checkin.week_number

    # -------------------------------------------------------------------------
    def num_distinct_checkins(self):
        # Note that only one check-in is considered per week. If multiple
        # check-ins happen during a week, they are just treated as one. The
        # number of keys in the distinct_checkin_type dictionary is an exact
        # count of distinct checkins since it tracts the weeks checked-in.
        return len(self.distinct_checkin_type.keys())
    
    # -------------------------------------------------------------------------
    def distinct_rf_checkin_proportion(self) -> int:
        """Returns the proportion of distinct checkins that were made using RF
        compared to the total number of distinct checkins"""
        rf_cnt = list(self.distinct_checkin_type.values()).count(RF_CHECKIN)
        return int(100.0 * rf_cnt / self.num_distinct_checkins())

    # -------------------------------------------------------------------------
    def net_participation(self) -> int:
        """Reports an AUXCs net participation over the period between the
        current week and the first recorded week that they joined the net."""
        return round(100 * self.num_distinct_checkins() /
                     (1 + (Auxc.current_week_number - self.first_checkin_week)))
    
    # -------------------------------------------------------------------------
    def weeks_since_last_checkin(self) -> int:
        return Auxc.current_week_number - max(self.distinct_checkin_type.keys())

    # -------------------------------------------------------------------------
    def checked_in_specified_week(self, week_number) -> bool:
        return week_number in self.distinct_checkin_type.keys()
    
    # -------------------------------------------------------------------------
    def __lt__(self, other):
        """AUXCs are sortable. They are ranked by the number of distinct
        checkins, then participation. More distinct checkins means an earier
        position in the overall list of AUXCs. If two or more AUXCs have the
        same number of distinct checkins and same level of participation, then
        they are sorted by callsign lexicographically."""

        if not isinstance(other, Auxc):
            raise TypeError(f'{self.callsign}: '\
                            'The other value is not an instance of Auxc')
        
        if self.num_distinct_checkins() == other.num_distinct_checkins():
            # Same number of distinct checkins, so check participation.
            if self.net_participation() == other.net_participation():
                # Same participation as well, order by callsign
                return self.callsign > other.callsign
            return self.net_participation() < other.net_participation()
        return self.num_distinct_checkins() < other.num_distinct_checkins()
     
    # -------------------------------------------------------------------------
    def __repr__(self):
        """This is the report. """
        # Even though this reporting system pulls out who is an AEC and adds it
        # to the appropriate Auxc instances - this is not currently used in the
        # report (it's done another way for convenience.)
        # aec_indicator = ''
        # if self.is_AEC:
        #     aec_indicator = 'Y'

        # The column arrangement must not be changed for this report.
        return f'{self.callsign}, ' \
               f'{self.num_distinct_checkins()}, '   \
               f'{self.net_participation()}, '       \
               f'{self.weeks_since_last_checkin()}, '\
               f'{self.distinct_rf_checkin_proportion()}, '   \
               f'{len(self.distinct_gateways)}'


    # -------------------------------------------------------------------------
    def __str__(self):
        return self.__repr__()
    
# -----------------------------------------------------------------------------
def checkins_by_callsign(checkins: list[Checkin]) -> dict[str, Auxc]:
    """Runs through all the checkins and arranges them by the operator's
    callsign
    
    Results in a dict, keyed by callsign. The value associated with a
    callsign is an Auxc object. Each Auxc has a list of check-ins. 
    
    """
    auxcs = {}
    for checkin in checkins:
        # Every AUXC is given a list to hold their checkins. Add any checkin for
        # that AUXC to their list.
        auxc = auxcs.setdefault(checkin.callsign.callsign, Auxc(checkin.callsign))
        auxc.add_checkin(checkin)
    return auxcs

# -----------------------------------------------------------------------------
def checkins_by_mode(checkins: list[Checkin]) -> list[(str, int)]:
    """Runs through all the checkins and arranges them by the transport mode
    used to check-in.
    
    Results in a sorted list. Each element is a mode name and count.
    """
    mode_counts = {}
    for checkin in checkins:
        transport_mode = checkin.transport_mode
        if checkin.is_mode_HF:
            transport_mode = 'HF'
        current_mode_count = mode_counts.setdefault(transport_mode, 0)
        mode_counts[transport_mode] = current_mode_count + 1
    
    sorted_mode_counts = sorted(mode_counts.items(),
                                key=lambda item: item[1], reverse=True)

    return sorted_mode_counts

def display_checkins_by_mode(mode_counts: dict[str, int]) -> None:
    print('Transport mode counts for all check-ins')
    total_checkins = sum([c[1] for c in mode_counts])
    for (mode, count) in mode_counts:
        proportion = count / float(total_checkins)
        print(f'{mode}, {count}, {proportion:.3f}')
    print(f'Total, {total_checkins}')
    
# -----------------------------------------------------------------------------
def checkin_count_by_week(auxcs: list[Auxc], start_week_num: int, 
                          n_previous: int) -> dict[int, int]:
    checkin_count_by_week = {}
    current_week_number = start_week_num
    for i in range(n_previous):
        checkin_count_by_week[current_week_number] = 0
        for auxc in auxcs:
            if auxc.checked_in_specified_week(current_week_number):
                checkin_count_by_week[current_week_number] += 1
        current_week_number -= 1
    return checkin_count_by_week

# -----------------------------------------------------------------------------
# Functions that print out a report component
# -----------------------------------------------------------------------------

def starlink_checkins(auxcs: dict[str, Auxc]) -> None:
    # The Starlink report - who has used Starlink whilst mobile.
    print("AUXCs that have checked in using Starlink while mobile:")
    starlink_auxcs = []
    for auxc in auxcs.values():
        if auxc.used_starlink > 0:
            starlink_auxcs.append(auxc)

    # Sort the list according to the number of times each AUXC used Starlink
    sorted_auxcs = sorted(starlink_auxcs,
                          key=lambda auxc: auxc.used_starlink, reverse=True)
    return sorted_auxcs

def display_starlink_checkins(starlink_auxcs: list[Auxc]) -> None:
    for star_auxc in starlink_auxcs:
        print(f'{star_auxc.callsign}, {star_auxc.used_starlink}')
    print()

# -----------------------------------------------------------------------------
def list_last_N_weeks_distinct(auxcs: dict[str, Auxc], n: int) -> None:
    # How many distinct check-ins for each of the previous N weeks?
    print(f'Distinct check-in counts for the Last {n} weeks')
    week_cnts = checkin_count_by_week(auxcs.values(), Checkin.max_week_number, 10)
    for week in sorted(week_cnts.keys(), reverse=True):
        print(f'{week}, {week_cnts[week]}')
    print()

# -----------------------------------------------------------------------------
def main():
    # Set up command line parsing.
    # Not implemented - use this one day to generate more date-flexible reports
    # (cl_num_header_lines, cl_raw_checkins_filename) = process_command_line()

    config.load_config_file('config.json')
    raw_checkins_filename = config.get_raw_checkin_filename()
    raw_checkins_col_names = config.get_raw_checkin_fieldnames()
    CARES_net_start_week_num = config.get_start_week_num()

    checkins = load_csv_file(raw_checkins_filename, 1,
                             raw_checkins_col_names,
                             CARES_net_start_week_num)

    (valid_checkins, invalid_checkins) = validate_checkins(checkins)

    # The CARES net has been running for this number of weeks. It started out as
    # the LOARES net, but was brought to the county as a whole two years after
    # its inception.
    net_operational_weeks = Checkin.max_week_number - CARES_net_start_week_num + 1

    # Set up the Auxc class before we start using instances of it.
    Auxc.net_running_weeks = net_operational_weeks
    Auxc.current_week_number = Checkin.max_week_number
    Auxc.aec_set = config.get_aecs()

    # List out the AUXCs' checkin information
    total_distinct_checkins = 0
    auxcs = checkins_by_callsign(valid_checkins)
    for auxc in sorted(auxcs.values(), reverse=True):
        total_distinct_checkins += auxc.num_distinct_checkins()
        print(auxc)
    print()

    #
    # Print out the summary information
    #
    print(f'The net has been running {net_operational_weeks} weeks\n')
    print(f'Total number of distinct check-ins after or including week '
          f'{CARES_net_start_week_num}: {total_distinct_checkins}\n')
    print(f'Total number of all checkins after or including week '
          f'{CARES_net_start_week_num}: {len(valid_checkins)}\n')
    
    # list distinct check-ins for the previous N weeks
    list_last_N_weeks_distinct(auxcs, 10)
    
    # List out the AUXCs who used Starlink to check-in whilst in the field
    display_starlink_checkins(starlink_checkins(auxcs))

    # The count of all check-ins by mode and ordered by the check-in count.
    display_checkins_by_mode(checkins_by_mode(valid_checkins))

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    main()