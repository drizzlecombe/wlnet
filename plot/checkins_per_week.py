import matplotlib as mpl
import matplotlib.pyplot as plt

import db_access as db

def _get_data_from_db(database_name: str) -> ([], []):
    db.start_database(database_name)

    q = """select week_number, count(*) 
             from (select distinct callsign, week_number
                                   from checkins)
            group by week_number"""
    db.query(q)
    db.close_database()
    return ([], [])
#------------------------------------------------------------------------------
def main(database_name: str) -> None:
    xy_data = _get_data_from_db(database_name)

#------------------------------------------------------------------------------
# Programme entry point
#------------------------------------------------------------------------------
if __name__ == '__main__':
    main('../db/checkins_test.db')