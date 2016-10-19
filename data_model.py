from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from geoalchemy2.types import Geography

Base = declarative_base()

class Point(Base):
     __tablename__ = 'Point'
     id = Column(Integer, primary_key=True)
     geom = Column(Geography(geometry_type='POINT', srid=4326))