from configparser import ConfigParser

import sqlalchemy as sa 
from sqlalchemy.orm import sessionmaker




def create_engine(connection_name, credentials_file_location='config.ini'):
    config = ConfigParser()
    config.read(credentials_file_location)
    host = config.get(connection_name, "host")
    driver = config.get(connection_name, "driver")
    database = config.get(connection_name, "database")
    username = config.get(connection_name, "username")
    password = config.get(connection_name, "password")
    db_type = config.get(connection_name, "db_type")

    if db_type == 'mysql':
        connection_string = f'mysql+mysqlconnector://{username}:{password}@{host}'
    elif db_type == 'sqlite':
        connection_string = f'sqlite:///{host}'
    elif db_type in ['postgres', 'postgresql']:
        connection_string = f'postgresql://{username}:{password}@{host}/{database}'
    elif db_type in ['mssql', 'sqlserver']:
        connection_string = f'mssql+pyodbc://{username}:{password}@{host}/{database}?driver={driver}'
    else: 
        raise ValueError('{db_type} is not a recognized db_type.')

    engine = sa.create_engine(connection_string)
    return engine