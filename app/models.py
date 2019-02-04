import logging, datetime, json

from sqlalchemy import MetaData, Table, Column, Integer, Date, Text
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func

from utilities.connections import create_engine
from utilities.format_address import format_address_street_type, format_address_direction


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('main.log')
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class DatabaseSession():
    def __init__(self, connection_name='production_db'):
        self.engine = create_engine(connection_name)
        self.metadata = MetaData()
        self.metadata.bind=self.engine
        self.metadata.reflect(self.engine)
        self.Base = automap_base(metadata=self.metadata)
        self.Base.prepare()

        self.Crime = self.Base.classes.crime
        self.ParcelSummary = self.Base.classes.parcel_summary
        self.PropertyAssessment = self.Base.classes.property_assessment
        # self.CrimeSummary = self.Base.classes.crime_summary
        # self.CrimeSummary = Table("crime_summary", self.metadata, autoload=True, autoload_with=self.engine)
        self.CrimeSummary = Table("crime_summary", self.metadata,
                Column("id", Integer, primary_key=True),
                Column("incident_date", Date),
                Column("neighborhood", Text),
                Column("crime_count", Integer),
                autoload=True,
                autoload_with=self.engine
        )

    
    def get_pid_by_address(self, address, zipcode=''):
        Session = sessionmaker(bind=self.engine) 
        session = Session()
        address_variant1 = format_address_street_type(address)
        address_variant2 = format_address_direction(address)
        address_variant3 = format_address_direction(address_variant1)
        pid = ''
        if zipcode:
            pid = session.query(self.PropertyAssessment.parcel_id).filter(
                func.lower(self.PropertyAssessment.address).in_([address, address_variant1, address_variant2, address_variant3]),
                self.PropertyAssessment.zip_code == zipcode
                ).first()
        if not pid:
            pid = session.query(self.PropertyAssessment.parcel_id).filter(
                func.lower(self.PropertyAssessment.address).in_([address, address_variant1, address_variant2, address_variant3])
                ).first()
        return pid[0]

    @staticmethod
    def convert_sa_object_to_dict(obj):
        fields = {}
        for field in [x for x in dir(obj) if not x.startswith('_') and x not in ['metadata', 'classes', 'prepare']]:
            data = obj.__getattribute__(field)
            fields[field] = data
        return fields

    def commit_session(self, session):
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(e)
            raise Exception(e)
        finally:
            session.close()
        return None


class Crime(DatabaseSession):
    def __init__(self, connection_name='production_db'):
        DatabaseSession.__init__(self, connection_name=connection_name)

    def insert_one_crime_record(self, incident_date, incident_number, neighborhood, street_address, description):
        crime = self.Crime(incident_date=incident_date, 
                        incident_number=incident_number, 
                        neighborhood=neighborhood, 
                        street_address=street_address, 
                        description=description)
        Session = sessionmaker(bind=self.engine) 
        session = Session()
        session.add(crime)
        self.commit_session(session)

    def insert_many_crime_records(self, crime_list):
        Session = sessionmaker(bind=self.engine) 
        session = Session()
        for crime in crime_list:
            crime_record = self.Crime(incident_date=crime.get('incident_date'), 
                        incident_number=crime.get('incident_number'), 
                        neighborhood=crime.get('neighborhood'), 
                        street_address=crime.get('street_address'), 
                        description=crime.get('description'),
                        scraping_input_date=crime.get('scraping_input_date'))
            session.add(crime_record)
        self.commit_session(session)

    def get_last_scraping_input_date(self):
        Session = sessionmaker(bind=self.engine) 
        session = Session()
        try:
            last_date = session.query(func.max(self.Crime.scraping_input_date)).first()
        except Exception as e:
            session.rollback()
            logger.error(e)
            raise Exception(e)
        finally:
            session.close()
        return last_date


class ParcelSummary(DatabaseSession):
    def __init__(self, connection_name='production_db'):
        DatabaseSession.__init__(self, connection_name=connection_name)
    
    def get_parcel_summary_by_pid(self, pid):
        Session = sessionmaker(bind=self.engine) 
        session = Session()
        parcel_summary = session.query(self.ParcelSummary).filter(self.ParcelSummary.parcel_id == pid).first()
        return parcel_summary
    
    def get_parcel_summary_dict_by_address(self, address, zipcode=''):
        pid = self.get_pid_by_address(address=address, zipcode=zipcode)
        result = self.get_parcel_summary_by_pid(pid)
        return self.convert_sa_object_to_dict(result)


class PropertyAssessment(DatabaseSession):
    def __init__(self, connection_name='production_db'):
        DatabaseSession.__init__(self, connection_name=connection_name)
    
    def get_property_assessment_by_pid(self, pid):
        Session = sessionmaker(bind=self.engine) 
        session = Session()
        property_assessment = session.query(self.PropertyAssessment).filter(self.PropertyAssessment.parcel_id == pid).first()
        return property_assessment
    
    def get_property_assessment_dict_by_address(self, address, zipcode=''):
        pid = self.get_pid_by_address(address=address, zipcode=zipcode)
        result = self.get_property_assessment_by_pid(pid)
        return self.convert_sa_object_to_dict(result)


class CrimeSummary(DatabaseSession):
    def __init__(self, connection_name='production_db'):
        DatabaseSession.__init__(self, connection_name=connection_name)

    def get_neighborhood_crime_count(self, start_date=None, end_date=None, neighborhoods=None):
        Session = sessionmaker(bind=self.engine) 
        session = Session()
        start_date = start_date if start_date else datetime.timedelta(days=365)
        end_date = end_date if end_date else datetime.datetime.now()
        if neighborhoods:
            neighborhoods = [neighborhood.lower() for neighborhood in neighborhoods]
            crime_count_list = session.query(self.CrimeSummary).filter(
                self.CrimeSummary.columns.incident_date >= start_date,
                self.CrimeSummary.columns.incident_date <= end_date,
                func.lower(self.CrimeSummary.columns.neighborhood).in_(neighborhoods)
            ).all()
        else: 
            crime_count_list = session.query(self.CrimeSummary).filter(
                self.CrimeSummary.columns.incident_date >= start_date,
                self.CrimeSummary.columns.incident_date <= end_date
            ).all()

        return crime_count_list