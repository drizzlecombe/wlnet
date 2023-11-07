import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
import db_access as db

BAR_COLOURS = ['black', 'black', 'black', 'black', 'black',
    'darkred', 'firebrick', 'red', 'orangered', 'darkorange',
                'orange', 'gold', 'yellow', 'greenyellow', 'limegreen',
                   'green', 'darkgreen', 'black']

# -----------------------------------------------------------------------------
def setup_pyplot():
    plt.rcParams['animation.ffmpeg_path'] = '..\\bin\\ffmpeg.exe'

# -----------------------------------------------------------------------------
def get_total_checkins_per_week(database_name: str) -> \
                                                tuple[list[int], list[int]]:
    db.start_database(database_name)

    q = """select week_number, count(*) 
             from (select distinct callsign, week_number
                     from checkins)
            group by week_number
            order by week_number asc"""
    
    result = db.query(q)
    db.close_database()

    week_numbers = [wd[0] for wd in result]
    week_counts = [wd[1] for wd in result]
    return week_numbers, week_counts

# -----------------------------------------------------------------------------
def main():
    
    setup_pyplot()

    fig, ax = plt.subplots(1, 1, figsize=(6, 4))


    ax.set_xlabel('Number of operators checking in for any week')
    ax.set_ylabel('Number of weeks')

    ax.yaxis.grid(True, linestyle='dotted')
    ax.set(xlim=(5, 18), xticks=range(5, 18), ylim=(0, 10), yticks=range(0, 10))

    writer = FFMpegWriter(fps=2)
    # Create each movie frame
    
    checkin_buckets_numbers = [i for i in range(0, 20)]
    checkin_buckets_totals = [0 for _ in range(0, 20)]

    (week_numbers, checkin_counts) = get_total_checkins_per_week('../db/checkins_week_52.db')
    
    with writer.saving(fig, "checkin_counts.mp4", 100):
        # Pause for a couple of seconds with no data in the bar chart
        for _ in range(0, 10):
            ax.set_title('Net participation (distinct operators/week): Week 0')
            ax.bar(checkin_buckets_numbers, checkin_buckets_totals, 
                linewidth=0.5, edgecolor='black', color=BAR_COLOURS)
            writer.grab_frame()

        # Plot the first line and cursor
        for week_number in week_numbers:
            ax.set_title('Net participation (distinct operators/week): '
                         f'Week {week_number}')
            current_bucket = checkin_counts[week_number - 1]
            bucket_contents = checkin_buckets_totals[current_bucket]
            checkin_buckets_totals[current_bucket] = bucket_contents + 1
            print(f'week_number: {week_number}, current bucket: {current_bucket}')
            ax.bar(checkin_buckets_numbers, checkin_buckets_totals, 
                linewidth=0.5, edgecolor='black', color=BAR_COLOURS)

            writer.grab_frame()

        # Spin for a few seconds on that last frame so it stays on screen
        for _ in range(0, 20):
            ax.set_title('Net participation (distinct operators/week):'
                         f' Week {week_number}')

            ax.bar(checkin_buckets_numbers, checkin_buckets_totals, 
                linewidth=0.5, edgecolor='black', color=BAR_COLOURS)
            writer.grab_frame()
# -----------------------------------------------------------------------------
# Programme entry point
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    main()

