create view sqft_by_neighborhood as
select ps.neighborhood, sum(pa.land_sqft) as sqft
from property_assessment as pa
join public.parcel_summary as ps
    on ps.parcel_id = pa.parcel_id
group by ps.neighborhood;