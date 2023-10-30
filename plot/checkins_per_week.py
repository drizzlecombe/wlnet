#------------------------------------------------------------------------------
# Experimental programme for generating a report from the checkins SQLite
# database. 
#------------------------------------------------------------------------------

import matplotlib as mpl
import matplotlib.pyplot as plt

import db_access as db

def _get_weekly_participation(database_name: str) -> [()]:
    db.start_database(database_name)

    q = """select week_number, count(*) 
             from (select distinct callsign, week_number
                                   from checkins)
            group by week_number"""
    result = db.query(q)
    db.close_database()
    return result

#------------------------------------------------------------------------------
def median(l: []) -> float:
    llen = len(l)
    if llen == 0:
        return 0.0
    sl = sorted(l)
    if llen % 2 == 0:
        return (float(sl[llen // 2 - 1]) + float(sl[llen // 2])) / 2.0
    return float(sl[llen // 2])

#------------------------------------------------------------------------------
def draw_chart(x: [], y: []) -> None:
    fig, ax = plt.subplots(1, 1, figsize=(10, 3))
    ax.plot(x, y, 'o:', ms='5', mec='1.0', linewidth='1.0', color='darkgreen', label='# checkins')
    ax.plot(x, [11] * len(x), '--', linewidth='1.0', color='darkred', label= 'mean')
    ax.set_title('Weekly participation in the LOARES Winlink net')
    ax.set_ylabel('Number of participants')
    ax.set_xlabel('Week number')
    ax.legend()
    plt.show()
#------------------------------------------------------------------------------
def main(database_name: str) -> None:
    xy_data = _get_weekly_participation(database_name)

    num_weeks = 0
    participant_total = 0
    wk_cnts = []
    week = []
    for (x, y) in xy_data:
        print(f'{x}, {y}')
        num_weeks += 1
        participant_total += y
        week.append(x)
        wk_cnts.append(y)
    mean_participation = float(participant_total) / float(num_weeks)
    print(f'Mean participation = {mean_participation: 0.2f}')
    print(f'Median participation = {median(wk_cnts): 0.2f}')
    draw_chart(week, wk_cnts)

#------------------------------------------------------------------------------
# Programme entry point
#------------------------------------------------------------------------------
if __name__ == '__main__':
    main('../db/checkins_test.db')