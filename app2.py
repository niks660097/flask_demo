from flask import jsonify
from geoalchemy2.elements import WKTElement
from geoalchemy2 import func
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from database_hanlder import connect_to_db, get_db_session
from data_model import Point

# Creates a Flask app and reads the settings from a
# configuration file. We then connect to the database specified
# in the settings file
app = Flask(__name__)
app.config.from_pyfile('app.cfg')#todo
engine = connect_to_db()

def get_within_radius(session, lat, lng, radius):
    geom_var = WKTElement('POINT({0} {1})'.format(lng, lat), srid=4326)
    return session.query(Point).filter(func.ST_DWithin, geom_var, radius).all()


@app.route('/co_ordinates/', methods=['GET', 'POST'])
def co_ordinates():
    if request.method == 'POST':
        lat = request.form['lat']
        lng = request.form['long']
        if lat and lng:
            point = WKTElement('POINT({0} {1})'.format(lng, lat), srid=4326)
            session = get_db_session(engine)
            p_obj = Point(geom=point)
            session.add(p_obj)
            session.commit()
            #todo response
            return jsonify({'status':'woriking'})

    if request.method == 'GET':
        lat = request.args.get('lat')
        lng = request.form('long')
        radius = request.form('radius')
        if lat and lng and radius:
            session = get_db_session(engine)
            result = get_within_radius(session, lat, lng, radius)
    return jsonify({'status': 'woriking'})

if __name__ == '__main__':
  # Run the app on all available interfaces on port 80 which is the
  # standard port for HTTP
	app.run(
        host="localhost",
        port=int("8000")
  )