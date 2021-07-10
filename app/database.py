from enum import auto
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'mscpw',
    'database': 'test-db'
}

db_user = config.get('user')
db_pwd = config.get('password')
db_host = config.get('host')
db_port = config.get('port')
db_name = config.get('database')

# specify connection string
connection_str = f'mysql+pymysql://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}'

engine = db.create_engine(connection_str)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
# table = db.Table('table', metadata, autoload=True, autoload_with=engine)

# query = db.select([table])
# ResultProxy = connection.execute(query)
# ResultSet = ResultProxy.fetchall()

# print(ResultSet[:])


