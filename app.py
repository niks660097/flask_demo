# # models.py
# class Post(db.Model):
#     __tablename__ = 'posts'
#     id = db.Column(db.Integer, primary_key=True)
#     location = db.Column(Geography(geometry_type='POINT', srid=4326))
#
# #routes.py
# from models import Post
#
# @app.route('/get_coordinates')
#     lat = request.args.get('lat', None)
#     lng = request.args.get('lng', None)
#
#     if lat and lng:
#         point = WKTElement('POINT({0} {1})'.format(lng, lat), srid=4326)
#         # Here i should make the query to get all Posts that are near the Point
#
# posts = db.session.query(Post).filter(func.ST_DWithin(Post.location, point, 10))