from sqlalchemy import *
from geoalchemy2.types import Geography

metadata = MetaData()

point_table = Table('Point', metadata,
    Column('id', Integer, primary_key=True),
    Column('geom', Geography(geometry_type='POINT', srid=4326), nullable=False),
)

