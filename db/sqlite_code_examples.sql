-- Creates the main table that holds distinct check-ins to the net
CREATE TABLE if not exists checkins(week_number INTEGER, 
                                       callsign TEXT, 
                                           mode TEXT, 
                                        gateway TEXT, 
                                      frequency REAL,
                                       location TEXT,
                                          state TEXT);


-- .mode changes the way the output is formatted. There are lots of options!
 .mode markdown
 .mode json
 .help mode

-- gets the number of distinct callsigns checking in for each week. 
select week_number, count(*)
  from (select distinct callsign, week_number 
          from checkins) 
 group by week_number;

-- gets the number of times each callsign checked in
-- TODO: may want to limit this to a specific time period (week_number between
-- 1 and 52). Remember, between is inclusive.
select callsign, count(*) 
 from (select distinct callsign, week_number
         from checkins)
 group by callsign;

--
-- TRANSPORT MODE QUERIES
--

-- get the count of all checkins for each transport mode. Limited by time span
select transport_mode, count(*)
  from checkins
 where week_number between 1 and 52
 group by transport_mode
 order by count(*);

-- Get the weekly count of checkins for a given transport mode.
-- Substitute 'VARA FM' for 'TELNET' or 'PACKET'
select week_number, count(*)
  from checkins
 where transport_mode = 'VARA FM'
 group by week_number order by week_number asc;
