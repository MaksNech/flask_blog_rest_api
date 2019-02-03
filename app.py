import os
import datetime
import uuid
import jwt
from functools import wraps
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from werkzeug.security import generate_password_hash, check_password_hash

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config.from_mapping(
    SECRET_KEY='dev',
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, 'db.sqlite'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

# Init DataBase
db = SQLAlchemy(app)

# Init Marshmallow
ma = Marshmallow(app)


# Begin Classes/Models #################################################################################################
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(100))
    admin = db.Column(db.Boolean)

    def __init__(self, username, public_id, password, admin):
        self.username = username
        self.public_id = public_id
        self.password = password
        self.admin = admin


# User serialization
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'public_id', 'username', 'password', 'admin')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String())
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    author_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    def __init__(self, title, body, created_at, author_id):
        self.title = title
        self.body = body
        self.created_at = created_at
        self.author_id = author_id


# Post serialization
class PostSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'body', 'created_at', 'author_id')


post_schema = PostSchema()
posts_schema = PostSchema(many=True)


# End Classes/Models ###################################################################################################

# Token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'msg': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'msg': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# Begin Routes/Views: ##################################################################################################
@app.route('/', methods=['GET'])
def index():
    result = {"msg": "Welcome to Flask Blog RESTfull App!"}
    return jsonify(result)
# Begin User bundle: ###################################################################################################
@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    if not current_user.admin:
        return jsonify({'msg': 'No rights to this action!'})

    users = User.query.all()
    result = {"msg": "List of all users!", "all_users": users_schema.dump(users)}
    return jsonify(result)


@app.route('/user/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'msg': 'No rights to this action!'})

    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({"msg": "User not found!"})
    else:
        result = {"msg": "User data information!", "user": user_schema.dump(user)}
        return jsonify(result)


@app.route('/user', methods=['POST'])
# If want to create first admin user should to comment: @token_required
# @token_required
def create_user():
    # if not current_user.admin:
    #     return jsonify({'msg': 'No rights to this action!'})

    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(public_id=str(uuid.uuid4()), username=data['username'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    result = {"msg": "New user created!", "user": user_schema.dump(new_user)}
    return jsonify(result)


@app.route('/user/<public_id>', methods=['PUT'])
# If want to set admin rights to user should to comment: @token_required
# @token_required
def set_admin_user(public_id):
    # if not current_user.admin:
    #     return jsonify({'msg': 'No rights to this action!'})

    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({"msg": "User not found!"})
    else:
        user.admin = True
        db.session.commit()
        result = {"msg": "Admins rights are set for the user!", "user": user_schema.dump(user)}
        return jsonify(result)


@app.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'msg': 'No rights to this action!'})

    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({"msg": "User not found!"})
    else:
        db.session.delete(user)
        db.session.commit()
        result = {"msg": "The user has been deleted!", "user": user_schema.dump(user)}
        return jsonify(result)


@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {"WWW-Authenticate": 'Basic realm="Login required!"'})

    user = User.query.filter_by(username=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {"WWW-Authenticate": 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)},
            app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify', 401, {"WWW-Authenticate": 'Basic realm="Login required!"'})


# End User Bundle ######################################################################################################
# Begin Post bundle: ###################################################################################################
@app.route('/post', methods=['GET'])
def get_all_posts():
    posts = Post.query.all()
    result = {"msg": "List of all posts!", "all_posts": posts_schema.dump(posts)}
    return jsonify(result)


@app.route('/post/own', methods=['GET'])
@token_required
def get_all_own_posts(current_user):
    posts = Post.query.filter_by(author_id=current_user.id).all()
    result = {"msg": "List of user`s own posts!", "all_own_posts": posts_schema.dump(posts)}
    return jsonify(result)


@app.route('/post/<post_id>', methods=['GET'])
@token_required
def get_one_post(current_user, post_id):
    post = Post.query.filter_by(id=post_id, author_id=current_user.id).first()

    if not post:
        return jsonify({'msg': 'Post not found!'})

    result = {"msg": "Post data information!", "post": post_schema.dump(post)}
    return jsonify(result)


@app.route('/post', methods=['POST'])
@token_required
def create_post(current_user):
    data = request.get_json()

    new_post = Post(title=data['title'], body=data['body'], created_at=datetime.datetime.utcnow(),
                    author_id=current_user.id)
    db.session.add(new_post)
    db.session.commit()

    result = {"msg": "New post created!", "post": post_schema.dump(new_post)}
    return jsonify(result)


@app.route('/post/<post_id>', methods=['PUT'])
@token_required
def change_post(current_user, post_id):
    new_data = request.get_json()
    post = Post.query.filter_by(id=post_id, author_id=current_user.id).first()

    if not post:
        return jsonify({'msg': 'Post not found!'})

    post.title = new_data['title']
    post.body = new_data['body']
    db.session.commit()

    result = {"msg": "Post was changed!", "post": post_schema.dump(post)}
    return jsonify(result)


@app.route('/post/<post_id>', methods=['DELETE'])
@token_required
def delete_post(current_user, post_id):
    post = Post.query.filter_by(id=post_id, author_id=current_user.id).first()

    if not post:
        return jsonify({'msg': 'Post not found!'})

    db.session.delete(post)
    db.session.commit()

    result = {"msg": "Post was deleted!", "post": post_schema.dump(post)}
    return jsonify(result)


# End Post Bundle ######################################################################################################
# End Routes/Views #####################################################################################################


# Run Server
if __name__ == '__main__':
    app.run(debug=True)
