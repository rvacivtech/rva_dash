create table postgres.public.property_assessment(
  id    serial  primary key,
  parcel_id    text,
  gpin    int,
  address_id    int,
  address    text,
  building_number    int,
  building_number_suffix    text,
  street_direction    text,
  street_name    text,
  street_type    text,
  zip_code    int,
  zip_plus    int,
  owner_name    text,
  assessment_mailing_address    text,
  assessment_mailing_city    text,
  assessment_mailing_state    text,
  assessment_mailing_zip_code    int,
  association_name    text,
  parent_pin    text,
  assessment_neighborhood_code    int,
  assessors_neighborhood_desc    text,
  property_classcode    int,
  property_class_description    text,
  corporation_id    int,
  land_sqft    numeric(10,2),
  state_plane_x_coordinate    numeric(14,6),
  state_plane_y_coordinate    numeric(14,6),
  assessment_date    date,
  land_value    money,
  dwelling_value    money,
  total_value    money,
  area_tax    numeric(10,2),
  jurisdiction_id    int,
  special_assessment_district    int,
  special_assessment_dist_desc    text,
  lat_lon    text
);

create index idx_parcel_id on public.property_assessment(parcel_id);

start transaction ;

DELETE
FROM
    public.property_assessment as pa1
        USING public.property_assessment as pa2
WHERE
    pa1.id > pa2.id
    AND pa1.parcel_id = pa2.parcel_id;

rollback;  --  commit