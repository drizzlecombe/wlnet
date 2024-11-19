#------------------------------------------------------------------------------
#
# Experimental programme for generating a report from the checkins CSV file
#
#------------------------------------------------------------------------------

import matplotlib as mpl
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

def _get_total_weekly_checkins(df: pd.DataFrame, start_week: int, stop_week: int) -> pd.Series:
    #
    # This function does the analogue of the following query but using
    # pandas and loading in a flat CSV file.
    #
    # select week_number, count(*) 
    #   from (select distinct callsign, week_number
    #           from checkins)
    #  group by week_number

    # Read the file content into a data frame. Note the following:
    #    Data and column labels have spaces after the seperator commas.
    #    This needs trimming out. Use skipinitialspace for this.
    #
    #    We use N/A in the file to indicate no RMS being used and for
    #    other reasons too. Pandas tries to convert these to NaN by 
    #    default. Setting keep_default_na prevents this behaviour.
    

    # Do the same query as the SQL in the comment above. This creates a
    # series with the index as callsign and the data column is a count.
    #
    # First:  return the rows between the start_week and stop_week
    #         numbers.
    # Second: select only the callsign and week_number columns
    # Third:  remove any callsign-week_number duplicate pairs as we only
    #         count one check-in per operator per week.
    # Fourth: Count the number of distinct checkins per week by grouping
    #         by week number then getting the size of this group (i.e.
    #         num entries) 

    assert start_week < stop_week, \
        "Start week number cannot be greater than the stop week number"
    
    checkin_counts = df[(df['week_number'] >= start_week) & (df['week_number'] <= stop_week)] \
                              [['callsign', 'week_number']] \
                                .drop_duplicates().groupby('week_number').size()
    return checkin_counts

#
# Similar to function above, but groupby('callsign')
def _get_total_distinct_checkins_by_callsign(df: pd.DataFrame, 
                                            start_week: int,
                                           stop_week: int) -> pd.Series:
    """Get the number of distinct weekly checkins per operator
    """

    assert start_week < stop_week, \
        "Start week number cannot be greater than the stop week number"

    checkin_counts = df[(df['week_number'] >= start_week) & (df['week_number'] <= stop_week)] \
                              [['callsign', 'week_number']] \
                                .drop_duplicates().groupby('callsign').size()
    return checkin_counts
#------------------------------------------------------------------------------
def exponential_smooth(data: list[int], smoothing_factor: float=0.30) -> list[float]:
    smoothed: list[float] = []
    smoothed.append(float(data[0]))
    for i in range(1, len(data)):
        val: float = smoothing_factor * data[i] + \
                    (1.0 - smoothing_factor) * smoothed[i - 1]
        smoothed.append(val)
    return smoothed

#------------------------------------------------------------------------------
def draw_checkins_per_week_chart(x: list[int], y: list[int], smoothed: list[float]) -> None:
    # Just one subplot in the figure. 
    fig, ax = plt.subplots(1, 1, figsize=(10, 4))
    # Plot the actual checkin values
    ax.plot(x, y, 'o:', ms='5', mec='1.0', linewidth='1.0', color='darkgreen', label='# checkins')
    # Plot the (hardwired) mean. TODO: Turn this into a function parameter
    ax.plot(x, [11] * len(x), '--', linewidth='1.0', color='darkred', label= 'mean')
    ax.plot(x, smoothed, '-', linewidth='1.0', color='blue', label='smoothed')
    ax.set_title('Weekly participation in the LOARES Winlink net')
    ax.set_ylabel('Number of participants')
    ax.set_xlabel('Week number')
    # Turn on the legend. Default placement is fine.
    ax.legend()
    plt.show()

#------------------------------------------------------------------------------
def draw_checkins_per_week_bar(num_checkins_dist: list[tuple[int, int]]) \
                                 -> None:
    """Draws a bar chart showing the sum of number of particpants/week
    
    num_chkins_dist - a list containing tuples. The tuples consist of:
       - count of checkins for a week
       - number of times that number of checkins occurred
    """
    # Just one subplot in the figure.
    fig, ax = plt.subplots(1, 1, figsize=(6, 4))
    
    # Hopefully this is enough colours for the number of bars in the chart. If
    # not , the colours will wrap.
    # TODO: Find a way of interpolating between darkred and darkgreen using
    # HTML colour codes.
    bar_colours = ['darkred', 'firebrick', 'red', 'orangered', 'darkorange',
               'orange', 'gold', 'yellow', 'greenyellow', 'limegreen',
               'green', 'darkgreen']
    
    # Has unzip() been deprecated?
    checkins_in_a_week = [k for (k, v) in num_checkins_dist]
    num_times_checkin_cnt_seen = [v for (k, v) in num_checkins_dist] 
    ax.bar(checkins_in_a_week, num_times_checkin_cnt_seen, 
           linewidth=0.5, edgecolor='black',
           color=bar_colours)
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    # Plot the actual checkin values
   
    ax.set_title('Weekly net participation (distinct operators/week)')
    ax.set_ylabel('Number of weeks')
    ax.set_xlabel('Number of operators checking in for any week')
    ax.yaxis.grid(True, linestyle='dotted')
    ax.set(xlim=(5, 18), xticks=range(5, 18),
       ylim=(0, 10), yticks=range(0, 10))
    plt.show()

# ------------------------------------------------------------------------------
def accumulate_week_counts(check_in_counts: pd.Series, n: int=4) -> pd.Series:
    """Accumulates week counts by n week periods

       n - the number of weeks in a period
    """
    week_cnt = 0
    period = 1
    period_counts = {}
    accumulated_checkin_counts = 0
    for week_checkins_count in check_in_counts:
        accumulated_checkin_counts += week_checkins_count
        week_cnt += 1
        if week_cnt == n:
            period_counts[period] = accumulated_checkin_counts
            period += 1
            accumulated_checkin_counts = 0
            week_cnt = 0
    return pd.Series(period_counts)

def draw_periodic_checkins_comparison(df: pd.DataFrame, period: int=4):
    """Creates a bar chart with bar groups for each of the two periods
    compared
    
    df - Pandas dataframe containing all checkins
    period - the number of weeks per period
    """
    year_one = _get_total_weekly_checkins(df, 1, 52)
    year_two = _get_total_weekly_checkins(df, 53, 104)

    year_one_compressed = accumulate_week_counts(year_one, period)
    year_two_compressed = accumulate_week_counts(year_two, period)
    
    # Match the data with labels in a way that bar charts like it
    # The labels start with 1 and go through to whatever length is needed.
    period_labels = np.array(year_one_compressed.index)

    # Just one subplot in the figure.
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))

    # There will be two bars in each bar group. 
    bar_width = 0.4
    bar_set = ax.bar(period_labels - bar_width/2,
                         year_one_compressed,
                         bar_width,
                         linewidth=0.5,
                         edgecolor='grey',
                         color='lightsteelblue',
                         label='Year One')
    ax.bar_label(bar_set, padding=3, fontsize=8)

    bar_set2 = ax.bar(period_labels + bar_width/2,
                     year_two_compressed,
                     bar_width,
                     linewidth=0.5,
                     edgecolor='grey',
                     color='orange',
                     label='Year Two')
    ax.bar_label(bar_set2, padding=3, fontsize=8)

    # Now some summary stats lines
    median_year_1 = year_one_compressed.median()
    ax.plot(period_labels, [median_year_1] * len(period_labels), 
            '--', linewidth='1.0',
            color='blue', label='median y1')
    
    median_year_2 = year_two_compressed.median()
    ax.plot(period_labels, [median_year_2] * len(period_labels),
            '--', linewidth='1.0',
            color='red', label='median y2')
    
    ax.set_title('Winlink net participation (distinct check-ins only)')
    ax.set_xlabel(f'Number of {period} week periods')
    ax.set_ylabel('Number of operators checking in per period')
    ax.yaxis.grid(True, linestyle='dotted')
    ax.set(xlim=(0, 14), xticks=range(0, 14),
           ylim=(30, 60), yticks=range(30, 60, 5))
    ax.legend(ncols=2)
    plt.show()

#------------------------------------------------------------------------------
def load_data_file(file_name: str) -> pd.DataFrame:
    """Load the raw individual check-ins into a Pandas DataFrame
    
    This is a straight load with minimal processing.
    """
    # Parameters to read_csv()
    #
    # skipinitialspace=True: Strips leading spaces from column names.
    # This allows us to refer to the column without having to remember
    # to add the spaces that were in the CSV file.
    #
    # keep_default_na=False: We use 'N/A' to indicate no RMS or city.
    # However, Pandas recognises 'N/A' and, by default, converts it to
    # NaN. Not the behaviour we want, so turn it off.

    df = pd.read_csv(file_name, skipinitialspace=True, keep_default_na=False) 
    
    # Remove the mobile operation suffix from any callsigns that has it appended.
    df['callsign'] = df['callsign'].str.replace('/M', '', regex=False)

    return df
#------------------------------------------------------------------------------
def main(data_file_name: str) -> None:

    df = load_data_file(data_file_name)
    checkin_count_year_one = _get_total_weekly_checkins(df, 0, 52)
    checkin_count_year_two = _get_total_weekly_checkins(df, 53, 104)


    draw_periodic_checkins_comparison(df)
    
    mean_participation = checkin_count_year_one.mean()
    median_participation = checkin_count_year_one.median()

    print(f'Mean participation = {mean_participation: 0.2f}')
    print(f'Median participation = {median_participation: 0.2f}')

#------------------------------------------------------------------------------
# Programme entry point
#------------------------------------------------------------------------------
if __name__ == '__main__':
    main('raw_data/all_checkins_loares_winlink_net.csv')
