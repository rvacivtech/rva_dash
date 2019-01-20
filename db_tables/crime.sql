create table postgres.public.crime (
  id     serial    primary key,
  incident_number   varchar(30),
  street_address   varchar(255),
  neighborhood    varchar(100),
  description     varchar(100),
  incident_date   timestamp
);
