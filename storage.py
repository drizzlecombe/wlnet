import sqlite3 as sql

_db_filename = None
_db_connection = None
_db_started = False
#------------------------------------------------------------------------------
class StorageException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

#------------------------------------------------------------------------------
def start_database(filename: str) -> None:
    global _db_filename, _db_connection, _db_started
    if not _db_started:       
        _db_filename = filename
        _db_connection = sql.connect(filename)
        _db_started = True

#------------------------------------------------------------------------------
def create_checkin_table() -> None:
    if not _db_started:
        raise StorageException('Cannot create a table when the DB is not running')
    cursor = _db_connection.cursor()
    cursor.execute("""
        CREATE TABLE if not exists checkins(
                    week_number INTEGER, 
                    callsign TEXT, 
                    transport_mode TEXT, 
                    gateway TEXT, 
                    frequency REAL,
                    location TEXT,
                    county TEXT,
                    state TEXT)""")
    _db_connection.commit()

#------------------------------------------------------------------------------
def close_database() -> None:
    if _db_started:
        _db_connection.close()

#------------------------------------------------------------------------------
def save_checkin(checkin: dict) -> None:
    if not _db_started:
        raise StorageException('Cannot save a checkin if the DB is not running')
    cursor = _db_connection.cursor()
    cursor.execute("""
                INSERT into checkins VALUES
                (:week_number,
                   :callsign,
                   :transport_mode,
                   :gateway,
                   :frequency,
                   :location,
                   :county,
                   :state)""", checkin)
    _db_connection.commit()
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------

__all__ = ['start_database','create_checkin_table',
           'save_checkin', 'close_database', 'StorageException']