#!/usr/bin/env python

# -----------------------------------------------------------------------------
#
# Prints out pre-validated check-ins for a given week neatly. 
#
# This tool uses a CSV file as input. As noted above, it is expected that the
# input CSV has been validated. For example, this programme does not check to
# see if frequencies, modes or suchlike are valid.
#
# However, this programme does expect the input CSV file to have eight columns
# and that those columns represent the following in the order listed:
#   Week number
#   Operator callsign
#   Transport mode
#   RMS station callsign (with SSID if the RMS uses one)
#   RMS station frequency
#   Operating location: City
#   Operating location: County / Province
#   Operating location: State / Country
#
# Author: Andrew Watson
# 
# -----------------------------------------------------------------------------

import csv
import enum
import sys
from typing import Tuple

# Number of lines in the CSV that are assumed to be headers. This could be an
# optional parameter on the command line.
NUM_HEADER_LINES = 1

# How many spaces used for padding? This many
PADDING = " "

SEPARATOR = ","
SEPARATOR_WIDTH = len(SEPARATOR)

# -----------------------------------------------------------------------------
class CSVFields(enum.Enum):
    WEEK_NUMBER = 0
    AUXC_CALLSIGN = 1
    TRANSPORT_MODE = 2
    RMS_CALLSIGN = 3
    RMS_FREQUENCY = 4
    AUXC_CITY = 5
    AUXC_COUNTY = 6
    AUXC_STATE = 7

# -----------------------------------------------------------------------------
def validate_week(week_number: str) -> int:
    value = 0
    try:
        value = int(week_number)
    except:
        raise ValueError(f"{sys.argv[0]}: Week number argument is not a number: {week_number}")
    
    if value < 1 or value > 1000:
        raise ValueError(f"{sys.argv[0]}: Week number is out of range: 1 < {week_number} < 1000")
# -----------------------------------------------------------------------------

def process_command_line() -> Tuple[str, str]:
    args_len = len(sys.argv)
    pname = sys.argv[0]
    week_number = 0
    file_name = ""
    if args_len == 3:
        week_number = validate_week(sys.argv[1])
        file_name = sys.argv[2]
    elif args_len < 3:
        raise ValueError(f"{pname}: Too few command line arguments")
    else:
        raise ValueError(f"{pname}: Too many command line arguments")

    return (sys.argv[1], file_name)

# -----------------------------------------------------------------------------
def load_csv_file(csv_file_name: str, num_header_lines: int, week_number: int = 1):
    
    raw_checkins = []
    with open(csv_file_name, "r", newline='') as csvfile:
        reader = csv.reader(csvfile)
        header_line_count = 0
        for checkin_line in reader:
            if header_line_count < num_header_lines:
                header_line_count += 1
                continue
            # Ignore checkins for invalid week numbers
            if int(checkin_line[0]) == week_number:
                raw_checkins.append(checkin_line)
    return raw_checkins

# -----------------------------------------------------------------------------
def strip_fields(week_rows):
    stripped_rows = []
    for row in week_rows:
        clean_row = []
        clean_row.append(row[CSVFields.WEEK_NUMBER.value].strip())
        clean_row.append(row[CSVFields.AUXC_CALLSIGN.value].strip())
        clean_row.append(row[CSVFields.TRANSPORT_MODE.value].strip())
        clean_row.append(row[CSVFields.RMS_CALLSIGN.value].strip())
        clean_row.append(row[CSVFields.RMS_FREQUENCY.value].strip())
        clean_row.append(row[CSVFields.AUXC_CITY.value].strip())
        clean_row.append(row[CSVFields.AUXC_COUNTY.value].strip())
        clean_row.append(row[CSVFields.AUXC_STATE.value].strip())
        stripped_rows.append(clean_row)
    return stripped_rows

# -----------------------------------------------------------------------------
def count_decimal_places(frequency: str) -> int:
    """
    Counts the number of decimal places in a string representing a floating
    point number (frequency)
    """
    if '.' in frequency:
        return len(frequency.split('.')[-1])
    else:
        return 0
    
# -----------------------------------------------------------------------------
def analyse_rows(week_rows):
    longest_week_number = 0
    longest_auxc_callsign = 0
    longest_transport_mode = 0
    longest_rms_callsign = 0
    most_rms_frequency_dps = 0

    for row in week_rows:
        week_number_len = len(row[CSVFields.WEEK_NUMBER.value])
        if week_number_len > longest_week_number:
            longest_week_number = week_number_len

        auxc_callsign_len = len(row[CSVFields.AUXC_CALLSIGN.value])
        if auxc_callsign_len > longest_auxc_callsign:
            longest_auxc_callsign = auxc_callsign_len

        transport_mode_len = len(row[CSVFields.TRANSPORT_MODE.value])
        if transport_mode_len > longest_transport_mode:
            longest_transport_mode = transport_mode_len

        rms_callsign_len = len(row[CSVFields.RMS_CALLSIGN.value])
        if rms_callsign_len > longest_rms_callsign:
            longest_rms_callsign = rms_callsign_len

        freq_dps = count_decimal_places(row[CSVFields.RMS_FREQUENCY.value])
        if freq_dps > most_rms_frequency_dps:
            most_rms_frequency_dps = freq_dps

    # print(f'Longest week number is {longest_week_number} characters')
    # print(f'Longest AUXC callsign is {longest_auxc_callsign} characters')
    # print(f'Longest transport mode is {longest_transport_mode} characters')
    # print(f'Longest RMS callsign is {longest_rms_callsign} characters')

    return [longest_week_number,
        longest_auxc_callsign,
        longest_transport_mode,
        longest_rms_callsign,
        most_rms_frequency_dps]
# -----------------------------------------------------------------------------
def pprint_rows(auxc_rows, field_lengths_max):
    for row in auxc_rows:
        # This is a little awkward because we do not use fixed widths for each
        # column in a row. A given column's width is set by the longest value
        # seen for that column plus some padding. 
        current_output_row = ""

        current_output_row += f"{row[CSVFields.WEEK_NUMBER.value]}{SEPARATOR}" \
            .ljust(field_lengths_max[CSVFields.WEEK_NUMBER.value] + SEPARATOR_WIDTH)
        
        current_output_row += PADDING

        current_output_row += f"{row[CSVFields.AUXC_CALLSIGN.value]}{SEPARATOR}" \
            .ljust(field_lengths_max[CSVFields.AUXC_CALLSIGN.value] + SEPARATOR_WIDTH)

        current_output_row += PADDING

        current_output_row += f"{row[CSVFields.TRANSPORT_MODE.value]}{SEPARATOR}" \
            .ljust(field_lengths_max[CSVFields.TRANSPORT_MODE.value] + SEPARATOR_WIDTH)

        current_output_row += PADDING

        current_output_row += f"{row[CSVFields.RMS_CALLSIGN.value]}{SEPARATOR}" \
            .ljust(field_lengths_max[CSVFields.RMS_CALLSIGN.value] + SEPARATOR_WIDTH)

        current_output_row += PADDING

        # Need to align the frequency - which is a floating point value - on the
        # decimal point. Usually, this will be 3 decimal places if everyone
        # checks in not using HF. If someone uses HF, then it is likely that
        # we'll have to accommodate four dps.
        freq = float(row[CSVFields.RMS_FREQUENCY.value])
        max_decimal_places = field_lengths_max[CSVFields.RMS_FREQUENCY.value]
        if max_decimal_places == 3:
            current_output_row += f"{freq:7.3f}{SEPARATOR}"
        elif max_decimal_places == 4:
            current_output_row += f"{freq:8.4f}{SEPARATOR}"

        current_output_row += PADDING

        # No consistency now for City, County, State because some names, like
        # Battle Ground are really long and mess up the formatting by
        # introducing a lot of white space.
        current_output_row += f"{row[CSVFields.AUXC_CITY.value]}{SEPARATOR}"
        current_output_row += PADDING
        current_output_row += f"{row[CSVFields.AUXC_COUNTY.value]}{SEPARATOR}"
        current_output_row += PADDING
        current_output_row += f"{row[CSVFields.AUXC_STATE.value]}"
        
        print(current_output_row)

# -----------------------------------------------------------------------------
# Programme entry point
# -----------------------------------------------------------------------------
if __name__ == '__main__':

    week_number, file_name = process_command_line()
    week_rows = load_csv_file(file_name, NUM_HEADER_LINES, int(week_number))
    clean_week_rows = strip_fields(week_rows)
    field_lengths_max = analyse_rows(clean_week_rows)
    pprint_rows(clean_week_rows, field_lengths_max)