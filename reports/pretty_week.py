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

import argparse
import csv
from enum import IntEnum
from operator import itemgetter
import sys

# Number of lines in the CSV that are assumed to be headers. This could be an
# optional parameter on the command line.
NUM_HEADER_LINES = 1

# How many spaces used for padding? This many
PADDING = " "

SEPARATOR = ","
SEPARATOR_WIDTH = len(SEPARATOR)

# -----------------------------------------------------------------------------
class DataField(IntEnum):
    WEEK_NUMBER = 0
    AUXC_CALLSIGN = 1
    TRANSPORT_MODE = 2
    RMS_CALLSIGN = 3
    RMS_FREQUENCY = 4
    AUXC_CITY = 5
    AUXC_COUNTY = 6
    AUXC_STATE = 7

# -----------------------------------------------------------------------------
def validate_week(week_number: int) -> int:
    if week_number < 1 or week_number > 1000:
        print(f"Error: {sys.argv[0]}: "
              f"Week number is out of range: 1 < {week_number} < 1000")
        sys.exit(2)
    return week_number

# -----------------------------------------------------------------------------
def validate_sort_columns(week_data: list[str]) -> list[tuple[int, bool]]:
    return [ # True means to reverse sort. 
            (DataField.TRANSPORT_MODE, True),
            (DataField.AUXC_CALLSIGN, False),
            (DataField.RMS_CALLSIGN, False)]

# -----------------------------------------------------------------------------

def process_command_line() -> tuple[list[tuple[int, bool]], int, str]:
    parser = argparse.ArgumentParser()
    # Positional arguments - these MUST be specified on the command line.
    parser.add_argument("week_number", help="The week number to list.", type=int)
    parser.add_argument("file_name", help="The file where the CSV data is stored.")
    
    # Optional arguments
    # -c or --column can be specified multiple times with multiple values.
    parser.add_argument("-c", "--column", action='append', type=str, 
                        help="Specifies a column to sort on. Multiple instances"
                        " are permitted.")

    args = parser.parse_args()
    sort_criteria = validate_sort_columns(args.column)
    week_number = validate_week(args.week_number)
    file_name = args.file_name

    return (sort_criteria, week_number, file_name)

# -----------------------------------------------------------------------------
def load_csv_file(csv_file_name: str, num_header_lines: int, 
                  week_number: int = 1) -> list[list[str]]:
    
    raw_checkins: list[list[str]] = []
    with open(csv_file_name, "r", newline='') as csv_file:
        reader = csv.reader(csv_file)
        header_line_count = 0
        for checkin_line in reader:
            if header_line_count < num_header_lines:
                header_line_count += 1
                continue
            # Only load lines from the CSV file that match the week number
            # specified.
            if int(checkin_line[0]) == week_number:
                raw_checkins.append(checkin_line)
    return raw_checkins

# -----------------------------------------------------------------------------
def clean_fields(week_rows: list[list[str]]) -> list[list[str]]:
    cleansed_rows = []
    for row in week_rows:
        clean_row = []
        clean_row.append(row[DataField.WEEK_NUMBER].strip())
        clean_row.append(row[DataField.AUXC_CALLSIGN].strip().upper())
        clean_row.append(row[DataField.TRANSPORT_MODE].strip().upper())
        clean_row.append(row[DataField.RMS_CALLSIGN].strip().upper())
        clean_row.append(row[DataField.RMS_FREQUENCY].strip())
        clean_row.append(row[DataField.AUXC_CITY].strip())
        clean_row.append(row[DataField.AUXC_COUNTY].strip())
        clean_row.append(row[DataField.AUXC_STATE].strip())
        cleansed_rows.append(clean_row)
    return cleansed_rows

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
def analyse_rows(week_rows: list[list[str]]) -> list[int]:
    longest_week_number: int = 0
    longest_auxc_callsign: int = 0
    longest_transport_mode: int = 0
    longest_rms_callsign: int = 0
    most_rms_frequency_dps: int = 0

    for row in week_rows:
        week_number_len = len(row[DataField.WEEK_NUMBER])
        if week_number_len > longest_week_number:
            longest_week_number = week_number_len

        auxc_callsign_len = len(row[DataField.AUXC_CALLSIGN])
        if auxc_callsign_len > longest_auxc_callsign:
            longest_auxc_callsign = auxc_callsign_len

        transport_mode_len = len(row[DataField.TRANSPORT_MODE])
        if transport_mode_len > longest_transport_mode:
            longest_transport_mode = transport_mode_len

        rms_callsign_len = len(row[DataField.RMS_CALLSIGN])
        if rms_callsign_len > longest_rms_callsign:
            longest_rms_callsign = rms_callsign_len

        freq_dps = count_decimal_places(row[DataField.RMS_FREQUENCY])
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
def freq_str_to_float(week_rows: list[list[str]]) -> list[list[str | float]]:
    converted_rows = [[
        row[DataField.WEEK_NUMBER],   \
        row[DataField.AUXC_CALLSIGN], \
        row[DataField.TRANSPORT_MODE],\
        row[DataField.RMS_CALLSIGN],  \
        float(row[DataField.RMS_FREQUENCY]), \
        row[DataField.AUXC_CITY],     \
        row[DataField.AUXC_COUNTY],   \
        row[DataField.AUXC_STATE]] for row in week_rows]
    return converted_rows


# -----------------------------------------------------------------------------
def sort_on_multiple_cols(week_rows: list[list[str | float]], 
                          sort_criteria: list[tuple[int, bool]]) \
                                        -> list[list [str | float]]:

    # Make a shallow copy so that we are not causing side effects (i.e. not
    # modifying the list that the reference passed in is pointing to)
    sort_data = week_rows.copy()

    # The columns are sorted in the reverse order that was specified by the
    # user. I do this because Python sorted() is stable - multiple records with
    # the same sort criterion are kept in the same order as as they were in the
    # original list.
    for column, reverse in reversed(sort_criteria):
        sort_data = sorted(sort_data, key=itemgetter(column), reverse=reverse)
    return sort_data

# -----------------------------------------------------------------------------
def pprint_rows(auxc_rows: list[list[str | float]], field_lengths_max: list[int]) -> None:
    for row in auxc_rows:
        # This is a little awkward because we do not use fixed widths for each
        # column in a row. A given column's width is set by the longest value
        # seen for that column plus some padding. 
        current_output_row = ""

        current_output_row += f"{row[DataField.WEEK_NUMBER]}{SEPARATOR}" \
            .ljust(field_lengths_max[DataField.WEEK_NUMBER] + SEPARATOR_WIDTH)
        
        current_output_row += PADDING

        current_output_row += f"{row[DataField.AUXC_CALLSIGN]}{SEPARATOR}" \
            .ljust(field_lengths_max[DataField.AUXC_CALLSIGN] + SEPARATOR_WIDTH)

        current_output_row += PADDING

        current_output_row += f"{row[DataField.TRANSPORT_MODE]}{SEPARATOR}" \
            .ljust(field_lengths_max[DataField.TRANSPORT_MODE] + SEPARATOR_WIDTH)

        current_output_row += PADDING

        current_output_row += f"{row[DataField.RMS_CALLSIGN]}{SEPARATOR}" \
            .ljust(field_lengths_max[DataField.RMS_CALLSIGN] + SEPARATOR_WIDTH)

        current_output_row += PADDING

        # Need to align the frequency column - which contains floating point
        # values - on the decimal point. Usually, this will be 3 decimal places
        # if everyone checks in not using HF. If someone uses HF, then it is
        # likely that we'll have to accommodate four dps.

        # Make sure this column really is a float (it should be, but just in
        # case)
        freq = float(row[DataField.RMS_FREQUENCY]) 
        max_decimal_places = field_lengths_max[DataField.RMS_FREQUENCY]
        if max_decimal_places == 3:
            current_output_row += f"{freq:7.3f}{SEPARATOR}"
        elif max_decimal_places == 4:
            current_output_row += f"{freq:8.4f}{SEPARATOR}"

        current_output_row += PADDING

        # No consistency now for City, County, State because some names, like
        # Battle Ground are really long and mess up the formatting by
        # introducing a lot of white space.
        current_output_row += f"{row[DataField.AUXC_CITY]}{SEPARATOR}"
        current_output_row += PADDING
        current_output_row += f"{row[DataField.AUXC_COUNTY]}{SEPARATOR}"
        current_output_row += PADDING
        current_output_row += f"{row[DataField.AUXC_STATE]}"
        
        print(current_output_row)

# -----------------------------------------------------------------------------
# Programme entry point
# -----------------------------------------------------------------------------
if __name__ == '__main__':

    sort_criteria, week_number, file_name = process_command_line()
    week_rows = load_csv_file(file_name, NUM_HEADER_LINES, week_number)
    clean_week_rows = clean_fields(week_rows)
    field_lengths_max = analyse_rows(clean_week_rows)

    # @TODO SORT ROWS IF USER REQUESTS HERE
    #
    # If a sort is requested, then need to convert the frequency column from
    # string to float. This will ensure that the correct ordering when a sort
    # includes a frequency component.
    fstf = freq_str_to_float(clean_week_rows)

    sorted_week_rows = sort_on_multiple_cols(fstf, sort_criteria)
    pprint_rows(sorted_week_rows, field_lengths_max)