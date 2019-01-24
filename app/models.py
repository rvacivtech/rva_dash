from sqlalchemy import MetaData, Table, Column, ForeignKey
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func

from utilities.connections import create_engine

class Database_Session():
    def __init__(self, connection_name='production_db'):
        self.engine = create_engine(connection_name)
        self.metadata = MetaData()
        self.metadata.reflect(self.engine)
        self.Base = automap_base(metadata=self.metadata)
        self.Base.prepare()

        self.Crime = self.Base.classes.crime


class Crime(Database_Session):
    def __init__(self, connection_name='production_db'):
        Database_Session.__init__(self, connection_name=connection_name)

    def insert_one_crime_record(self, incident_date, incident_number, neighborhood, street_address, description):
        crime = self.Crime(incident_date=incident_date, 
                        incident_number=incident_number, 
                        neighborhood=neighborhood, 
                        street_address=street_address, 
                        description=description)
        Session = sessionmaker(bind=self.engine) 
        session = Session()
        session.add(crime)
        session.commit()

    def insert_many_crime_records(self, crime_list):
        Session = sessionmaker(bind=self.engine) 
        session = Session()
        for crime in crime_list:
            crime_record = self.Crime(incident_date=crime.get('incident_date'), 
                        incident_number=crime.get('incident_number'), 
                        neighborhood=crime.get('neighborhood'), 
                        street_address=crime.get('street_address'), 
                        description=crime.get('description'))
            session.add(crime_record)
        session.commit()

    def get_last_scraping_input_date(self):
        Session = sessionmaker(bind=self.engine) 
        session = Session()
        last_date = session.query(func.max(self.Crime.scraping_input_date)).first()
        return last_date

class Parcel_Summary(Database_Session):
    def __init__(self, connection_name='production_db'):
        Database_Session.__init__(self, connection_name=connection_name)
    
