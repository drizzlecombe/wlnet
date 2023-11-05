-- Creates the main table that holds distinct check-ins to the net
CREATE TABLE if not exists checkins(week_number INTEGER, 
                                       callsign TEXT, 
                                           mode TEXT, 
                                        gateway TEXT, 
                                      frequency REAL,
                                       location TEXT,
                                          state TEXT);

-- Maps callsigns used to checkin to new callsigns received after the checkin
-- was made. Most callsigns will map directly onto themselves.
CREATE TABLE if not exists callsign_map(checkin_callsign TEXT, 
                                        current_callsign TEXT);

INSERT INTO callsign_map (checkin_callsign, current_callsign)
VALUES
('AD7EF', 'AD7EF'),
('K0AXS', 'K0AXS'),
('KD7DNM', 'KD7DNM'),
('KD7PFH', 'KD7PFH'),
('KF7KXX', 'KF7KXX'),
('KI7LAG', 'KI7LAG'),
('KJ7JBE', 'KJ7JBE'),
('KJ7JCR', 'KJ7JCR'),
('KJ7YYW', 'W6RKT'),
('N1ACW', 'N1ACW'),
('WA6DOZ', 'WA6DOZ'),
('WA6GBW', 'WA6GBW'),
('WA6ZLV', 'WA6ZLV'),
('WH6EWE', 'WH6EWE'),
('KF0RST', 'KF0RST'),
('KI7DGC', 'KI7DGC'),
('N7LIM', 'N7LIM'),
('WA1TRH', 'WA1TRH'),
('W6AGZ', 'W6AGZ'),
('KK7JZB', 'W3STM'),
('KK7MLS', 'KK7MLS'),
('AI7MI', 'AI7MI'),
('W7MML', 'W7MML'),
('W3STM', 'W3STM'),
('W6RKT', 'W6RKT');

-- .mode changes the way the output is formatted. There are lots of options!
 .mode markdown
 .mode json
 .help mode

-- gets the number of distinct callsigns checking in for each week. 
-- Note that the subquery is important because this limits/filters multiple
-- checkins for an individual week. So if N0CAL checked in three times, the
-- subquery acknowledges just one checkin for the week.
select week_number, count(*)
  from (select distinct callsign, week_number 
          from checkins) 
 group by week_number;

-- gets the number of times each callsign checked in. Only count one check-in
-- per week.
-- TODO: may want to limit this to a specific time period (week_number between
-- 1 and 52). Remember, between is inclusive.
select callsign, count(*) 
  from (select distinct callsign, week_number
          from checkins)
 group by callsign
 order by count(*) desc;

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

-- Create a list of the number of checkins made using each transport mode used
-- by each individual operator. The subquery find each week that a given
-- callsign checks in at least once using a specific transport mode. This is
-- true even if the operator checks in more than once using a specific
-- transport mode, like VARA FM, during a specific week. 
select cs, mode, count(*)
  from (select distinct cm.current_callsign as cs, 
                        transport_mode as mode, 
                        week_number
          from checkins, callsign_map as cm
         where checkins.callsign = cm.checkin_callsign) 
 group by cs, mode
 order by cs, mode;

