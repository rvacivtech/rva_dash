from sqlalchemy import MetaData, Table, Column, ForeignKey
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

from utilities.connections import create_engine

engine = create_engine('production_db')

# produce our own MetaData object
metadata = MetaData()

# we can reflect it ourselves from a database, using options
# such as 'only' to limit what tables we look at...
metadata.reflect(engine)

# we can then produce a set of mappings from this MetaData.
Base = automap_base(metadata=metadata)

# calling prepare() just sets up mapped classes and relationships.
Base.prepare()

# mapped classes are ready
Crime = Base.classes.crime



def insert_one_crime_record(incident_date, incident_number, neighborhood, street_address, description):
    crime = Crime(incident_date=incident_date, 
                    incident_number=incident_number, 
                    neighborhood=neighborhood, 
                    street_address=street_address, 
                    description=description)
    Session = sessionmaker(bind=engine) 
    session = Session()
    session.add(crime)
    session.commit()


def insert_many_crime_records(crime_list):
    Session = sessionmaker(bind=engine) 
    session = Session()
    for crime in crime_list:
        crime_record = Crime(incident_date=crime.get('incident_date'), 
                    incident_number=crime.get('incident_number'), 
                    neighborhood=crime.get('neighborhood'), 
                    street_address=crime.get('street_address'), 
                    description=crime.get('description'))
        session.add(crime_record)
    session.commit()
