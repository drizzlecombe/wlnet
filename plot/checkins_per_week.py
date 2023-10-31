#------------------------------------------------------------------------------
# Experimental programme for generating a report from the checkins SQLite
# database. 
#------------------------------------------------------------------------------

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import db_access as db

def _get_total_checkins_per_week(database_name: str) -> list[tuple[int, int]]:
    db.start_database(database_name)

    q = """select week_number, count(*) 
             from (select distinct callsign, week_number
                                   from checkins)
            group by week_number"""
    result = db.query(q)
    db.close_database()
    return result

#------------------------------------------------------------------------------
def median(l: list[int]) -> float:
    llen = len(l)
    if llen == 0:
        return 0.0
    sl = sorted(l)
    if llen % 2 == 0:
        return (float(sl[llen // 2 - 1]) + float(sl[llen // 2])) / 2.0
    return float(sl[llen // 2])

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

#------------------------------------------------------------------------------#------------------------------------------------------------------------------
def main(database_name: str) -> None:
    checkins_by_week_num = _get_total_checkins_per_week(database_name)

    num_weeks = 0
    participant_total = 0
    week_numbers: list[int] = []
    week_checkin_counts: list[int] = []
    aggregated_checkin_counts = {}
    for (week_no, num_checkins) in checkins_by_week_num:
        print(f'{week_no}, {num_checkins}')
        num_weeks += 1
        participant_total += num_checkins
        week_numbers.append(week_no)
        week_checkin_counts.append(num_checkins)

        # Count the weeks that have exactly n checkins.
        week_count = aggregated_checkin_counts.setdefault(num_checkins, 0)
        week_count += 1
        aggregated_checkin_counts[num_checkins] = week_count

    smoothed_week_counts: list[float] = exponential_smooth(week_checkin_counts)    
    mean_participation = float(participant_total) / float(num_weeks)
    
    # Sort the number of checkins per week seen. Answers the question: 'How
    # weeks seen n checkins?' 
    sorted_times_seen_counts = [(k, aggregated_checkin_counts[k]) \
                                for k in \
                                    sorted(aggregated_checkin_counts.keys())]

    print(f'Mean participation = {mean_participation: 0.2f}')
    print(f'Median participation = {median(week_checkin_counts): 0.2f}')
    print(f'Aggregate checkins: {sorted_times_seen_counts}')
    draw_checkins_per_week_chart(week_numbers, week_checkin_counts,
                                 smoothed_week_counts)
    draw_checkins_per_week_bar(sorted_times_seen_counts)
#------------------------------------------------------------------------------
# Programme entry point
#------------------------------------------------------------------------------
if __name__ == '__main__':
    main('../db/checkins_test.db')