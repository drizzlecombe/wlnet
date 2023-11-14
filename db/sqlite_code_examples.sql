-- Creates the main table that holds distinct check-ins to the net
CREATE TABLE if not exists checkins(week_number INTEGER, 
                                       callsign TEXT, 
                                           mode TEXT, 
                                        gateway TEXT, 
                                      frequency REAL,
                                  neighbourhood TEXT,
                                         county TEXT,
                                          state TEXT);



-- .mode changes the way the output is formatted. There are lots of options!
 .mode markdown
 .mode json
 .help mode

--
-- The number of callsigns checking in over a specific period in total
--
select count(*)
  from (select distinct callsign, week_number 
          from checkins
          where week_number between 1 and 52);

-- Number of duplicate checkins in a period.
 select sum(cnt)
   from (select callsign, week_number, count(*) as cnt 
           from checkins 
          group by callsign, week_number
         having count(*) > 1);

-- gets the number of distinct callsigns checking in for each week. 
-- Note that the subquery is important because this limits/filters multiple
-- checkins for an individual week. So if N0CAL checked in three times, the
-- subquery acknowledges just one checkin for the week.
select week_number, count(*)
  from (select distinct callsign, week_number 
          from checkins
          where week_number between 1 and 52) 
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

-- Which neighbourhoods are busiest in the net? Remember that operators
-- checking in from outside Lake Oswego have the neighbourhood assigned as N/A.
-- Note that this query is limited to the first year of operation.
select neighbourhood as nh, count(*) as c 
  from (select distinct week_number, callsign, neighbourhood 
                   from checkins
                  where week_number between 1 and 52)
 where nh != 'N/A' 
 group by nh 
 order by c desc;

--
-- TRANSPORT MODE QUERIES
--

-- get the count of all the distinct checkins for each transport mode. Limited
-- by time span
select t, count(*) 
 from (select distinct callsign, week_number, transport_mode as t 
         from checkins
        where week_number
      between 1 and 52)
group by t 
order by count(*) desc;

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
  from (select distinct callsign as cs, 
                        transport_mode as mode, 
                        week_number
          from checkins) 
 group by cs, mode
 order by cs, mode;

