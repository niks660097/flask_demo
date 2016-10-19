from flask import jsonify, session, request
from geoalchemy2.elements import WKTElement
from sqlalchemy import func
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from database_handler import connect_to_db, get_db_session
from data_model import Point
from werkzeug.security import gen_salt
from flask_oauthlib.provider import OAuth1Provider
from shapely import wkb

# Creates a Flask app and reads the settings from a
# configuration file. We then connect to the database specified
# in the settings file
app = Flask(__name__)
app.config.from_pyfile('app.cfg')#todo
#todo oauth
# db = SQLAlchemy(app)
#
#
# def current_user():
#     if 'id' in session:
#         uid = session['id']
#         return User.query.get(uid)
#     return None


engine = connect_to_db()

def get_within_radius(session, lat, lng, radius):
    geom_var = WKTElement('POINT({0} {1})'.format(lng, lat), srid=4326)
    return session.query(Point).filter(func.ST_DWithin(Point.geom, geom_var, radius)).all()

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
            return jsonify({'status': 'added'})

    if request.method == 'GET':
        lat = request.args.get('lat')
        lng = request.args.get('long')
        radius = request.args.get('radius')
        if lat and lng and radius:
            session = get_db_session(engine)
            result = get_within_radius(session, lat, lng, radius)
            final_res = {'data': []}
            for i in result:
                point = wkb.loads(bytes(i.geom.data))
                final_res['data'].append([point.x,point.y])
            print(final_res)
            return jsonify(final_res)

if __name__ == '__main__':
  # Run the app on all available interfaces on port 80 which is the
  # standard port for HTTP
	app.run(
        host="localhost",
        port=int("8000")
  )