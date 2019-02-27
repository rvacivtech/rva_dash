create view neighborhood_facts as
select ps.neighborhood,
       avg(pa.land_value::numeric/pa.land_sqft)::money as average_land_value_per_sqft,
       avg(pa.total_value::numeric)::money as average_property_value,
       round(c.crime_per_10000_sqft,2) as relative_crime_rate
from public.property_assessment as pa
join public.parcel_summary as ps
    on ps.parcel_id = pa.parcel_id
join public.crime_per_sqft_by_neighborhood as c
    on lower(c.neighborhood) = lower(ps.neighborhood)
where pa.land_sqft > 0
group by ps.neighborhood, c.crime_per_10000_sqft
order by 2 desc;