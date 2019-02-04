create view crime_summary as
select row_number() over (order by c.incident_date::timestamp::date, c.neighborhood) as id, c.incident_date::timestamp::date, coalesce(c.neighborhood, 'ALL NEIGHBORHOODS') as neighborhood, count(c.incident_number) as crime_count
from postgres.public.crime as c
group by rollup(c.incident_date::timestamp::date, c.neighborhood)
order by 1;