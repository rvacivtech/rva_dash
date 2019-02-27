create view crime_per_sqft_by_neighborhood as
select c.neighborhood,
       count(distinct c.incident_number) as crime_count,
       s.sqft,
       count(distinct c.incident_number)/s.sqft*100000 as crime_per_10000_sqft
from public.crime as c
join sqft_by_neighborhood as s
    on lower(s.neighborhood) = lower(c.neighborhood)
where c.incident_date > current_date - interval '1 year'
group by c.neighborhood, s.sqft
order by 4;