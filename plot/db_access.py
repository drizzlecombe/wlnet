import sqlite3 as sql

_db_filename = None
_db_connection = None
_db_started = False

#------------------------------------------------------------------------------
def start_database(filename: str) -> None:
    global _db_filename, _db_connection, _db_started
    if not _db_started:       
        _db_filename = filename
        _db_connection = sql.connect(filename)
        _db_started = True

#------------------------------------------------------------------------------
def close_database() -> None:
    if _db_started:
        _db_connection.close()

#------------------------------------------------------------------------------
def query(sqlquery: str) -> None:
    if not _db_started:
        raise Exception('Cannot run query if the DB is not running')
    cursor = _db_connection.cursor()
    cursor.execute(sqlquery)
    print(cursor.fetchall())
#------------------------------------------------------------------------------

__all__ = ['start_database', 'close_database', 'query']