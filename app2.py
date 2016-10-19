import hmac
import hashlib
import base64
import uuid
from geoalchemy2.elements import WKTElement
from sqlalchemy import func
from database_handler import connect_to_db, get_db_session
from data_model import Point
from shapely import wkb
from datetime import datetime, timedelta
from flask import Flask
from flask import session, request
from flask import render_template, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import gen_salt
from flask_oauthlib.provider import OAuth2Provider

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


#OAUth code
db = SQLAlchemy(app)
oauth = OAuth2Provider(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)


class Client(db.Model):
    client_id = db.Column(db.Integer, primary_key=True)
    client_secret = db.Column(db.String(55), nullable=False)

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.Integer, db.ForeignKey('client.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')

    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id')
    )
    user = db.relationship('User')
    access_token = db.Column(db.String(255), unique=True)

def current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None

def get_access_token(client,user):
    msg = '%s:%s:%s' %(user.username, client.client_id, client.client_secret)
    dig = hmac.new(b'1234567890', msg=msg.encode('utf-8'), digestmod=hashlib.sha256).digest()
    return base64.b64encode(dig).decode()

def decode_access_token(token):



@app.route('/client/', methods=['POST'])
def create_client():
    if request.method == 'POST':
        client_secret = str(uuid.uuid1())#unique id based on timestamp and host
        client = Client(client_secret=client_secret)
        db.session.add(client)
        db.session.commit()
        client = Client.query.filter_by(client_secret=client_secret).first()
        return jsonify({'client_secret': client_secret, 'client_id': client.client_id})#sending as response

@app.route('/rest/oauth/token/', methods=['POST'])
def oauth_token():
    if request.method == 'POST':
        client_id = request.form.get('client_id')
        client_secret = request.form.get('client_secret')
        client = Client.query.filter_by(client_id=client_id, client_secret=client_secret).first()
        if not client:
            return jsonify({'status': 'Client not found!'})
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
        if not user:#no password
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
        session['id'] = user.id#grant process skipped#internal
        access_token = get_access_token(client, User.query.filter_by(username=username).first())
        token = Token(client_id=client_id, user_id=session['id'], access_token=access_token)
        db.session.add(token)
        db.session.commit()
        return jsonify({'access_token': access_token})

def enforce_oauth(func):
    def wrapped(*args, **kwargs):
        access_token = request.headers.get('Authorization')
        if not access_token:
            return jsonify({'status': 'Invalid request!'})
        user = current_user()
        token = Token.query.filter_by(access_token=access_token).first()
        # import pdb;pdb.set_trace()
        if not token:
            return jsonify({'status': 'Invalid user!'})
        return func(*args, **kwargs)
    return wrapped
#oauthcode end

# engine = connect_to_db()

def get_within_radius(session, lat, lng, radius):
    geom_var = WKTElement('POINT({0} {1})'.format(lng, lat), srid=4326)
    return session.query(Point).filter(func.ST_DWithin(Point.geom, geom_var, radius)).all()


@app.route('/test/oauth/', methods=['GET'])
@enforce_oauth
def test_oauth():
    return jsonify({'status': 'Working'})

@app.route('/co_ordinates/', methods=['GET', 'POST'])
@enforce_oauth
def co_ordinates():
    if request.method == 'POST':
        lat = request.form['lat']
        lng = request.form['long']
        if lat and lng:
            point = WKTElement('POINT({0} {1})'.format(lng, lat), srid=4326)
            p_obj = Point(geom=point)
            db.session.add(p_obj)
            db.session.commit()
            return jsonify({'status': 'added'})

    if request.method == 'GET':
        lat = request.args.get('lat')
        lng = request.args.get('long')
        radius = request.args.get('radius')
        if lat and lng and radius:
            result = get_within_radius(db.session, lat, lng, radius)
            final_res = {'data': []}
            for i in result:
                point = wkb.loads(bytes(i.geom.data))
                final_res['data'].append([point.x,point.y])
            print(final_res)
            return jsonify(final_res)

if __name__ == '__main__':
  # Run the app on all available interfaces on port 80 which is the
  # standard port for HTTP
    db.create_all()
    app.run(
        host="localhost",
        port=int("8000")
  )