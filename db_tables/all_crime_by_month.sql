create view all_crime_by_month as
select row_number() over (order by date_part('year', cs.incident_date), date_part('month', cs.incident_date)) as id,
        cast(date_part('year', cs.incident_date) as INTEGER) as year,
        cast(date_part('month', cs.incident_date) as INTEGER) as month,
        concat(date_part('month', cs.incident_date), '/', date_part('year', cs.incident_date)) as date,
        sum(distinct cs.crime_count) as number_of_crimes
from postgres.public.crime_summary as cs
where cs.neighborhood = 'ALL NEIGHBORHOODS'
and cs.incident_date > '2018-01-01'
group by date_part('year', cs.incident_date), date_part('month', cs.incident_date)
order by date_part('year', cs.incident_date), date_part('month', cs.incident_date);