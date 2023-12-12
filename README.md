# How to run this check-in processor

- Edit config.json to point to the desired output database. Currently this is
  set to checkins_week_test.db. Never check this database into git - always
  delete it at the end of a session.
- Run python checkin_manager.py

You should see each checkin line scroll by on the screen. Failures happen
immediately, so if there is a broken check-in, then the script will abort.