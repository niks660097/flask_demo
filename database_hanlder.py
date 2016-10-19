from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def connect_to_db():
    engine = create_engine('postgresql://gis:gis@localhost/gis', echo=True)
    return engine

def create_table(table, engine):
    table.create(engine)


def get_db_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    return session