import os
from flask import Flask
from flask import redirect, render_template, request, session, url_for
from flask_oauthlib.client import OAuth
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    twitter_id = db.Column(db.String(80), unique=True)
    twitter_name = db.Column(db.String(80), unique=True)
    tokens = db.relationship('Token', backref='user', lazy='dynamic')


class Pin(db.Model):
    __tablename__ = 'pins'

    id = db.Column(db.Integer, primary_key=True)
    twitter_name = db.Column(db.String(80))
    text = db.Column(db.String(140))
    image = db.Column(db.String(140))


class Token(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(40))
    oauth_token = db.Column(db.String(120))
    oauth_token_secret = db.Column(db.String(120))


@app.before_first_request
def create_tables():
    db.create_all()


oauth = OAuth()
twitter = oauth.remote_app(name='twitter',
                           base_url='https://api.twitter.com/1/',
                           request_token_url='https://api.twitter.com/oauth/request_token',
                           access_token_url='https://api.twitter.com/oauth/access_token',
                           authorize_url='https://api.twitter.com/oauth/authenticate',
                           consumer_key=os.environ['TWITTER_KEY'],
                           consumer_secret=os.environ['TWITTER_SECRET']
                           )


@twitter.tokengetter
def get_twitter_token(token=None):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    twitter_token = Token.query.filter_by(user=user, name='Twitter').first()
    return (twitter_token.oauth_token, twitter_token.oauth_token_secret)


# Login Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            return f(*args, **kwargs)
        return redirect(url_for('login'))
    return decorated_function


app_name = 'Pinterest Clone'

@app.route('/')
def home():
    twitter_name = session.get('twitter_name')
    images = Pin.query.all()
    return render_template('grid.html',
            title='All images', app_name=app_name, images=images, user=twitter_name)


@app.route('/myimages')
@login_required
def my_images():
    twitter_name = session.get('twitter_name')
    images = Pin.query.filter_by(twitter_name=twitter_name).all()
    return render_template('grid.html',
            title='My images', app_name=app_name, images=images, user=twitter_name)


@app.route('/newimage', methods=['POST'])
@login_required
def post_image():
    twitter_name = session['twitter_name']
    image_url = request.form.get('image_url')
    image_text = request.form.get('image_text')

    if twitter_name and image_url and image_text:
        new_pin = Pin(twitter_name=twitter_name, text=image_text, image=image_url)
        db.session.add(new_pin)
        db.session.commit()

    return redirect(request.referrer or url_for('home'))

@app.route('/deleteimage/<pin_id>')
@login_required
def delete_image(pin_id):
    twitter_name = session['twitter_name']
    pin = Pin.query.get(pin_id)

    if pin.twitter_name == twitter_name:
        db.session.delete(pin)
        db.session.commit()

    return redirect(request.referrer or url_for('home'))


@app.route('/login')
def login():
    return render_template('login.html', title='Login', app_name=app_name)


@app.route('/auth/twitter')
def twitter_auth():
    return twitter.authorize(callback=url_for('twitter_auth_callback'), next=None)


@app.route('/auth/twitter/callback')
def twitter_auth_callback():
    next_url = url_for('home')
    resp = twitter.authorized_response()

    if resp is None:
        print('Error: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        ))
        return redirect(next_url)

    twitter_name = resp['screen_name']
    twitter_id = resp['user_id']
    oauth_token = resp['oauth_token']
    oauth_token_secret = resp['oauth_token_secret']

    user = User.query.filter_by(twitter_id=twitter_id).first()

    # Twitter Name associated with Twitter Id can be changed
    if user:
        if user.twitter_name != twitter_name:
            user.twitter_name = twitter_name
            db.session.commit()
        twitter_token = Token.query.filter_by(
            user=user, name='Twitter').first()

    else:
        new_user = User(twitter_id=twitter_id, twitter_name=twitter_name)
        db.session.add(new_user)
        db.session.commit()

    user = User.query.filter_by(twitter_id=twitter_id).first()
    twitter_token = Token.query.filter_by(user=user, name='Twitter').first()
    if twitter_token:
        twitter_token.oauth_token = oauth_token
        twitter_token.oauth_token_secret = oauth_token_secret
        db.session.commit()
    else:
        twitter_token = Token(name='Twitter', oauth_token=oauth_token,
                              oauth_token_secret=oauth_token_secret, user=user)
        db.session.add(twitter_token)
        db.session.commit()

    session['user_id'] = user.id
    session['twitter_id'] = twitter_id
    session['twitter_name'] = twitter_name

    return redirect(next_url)


@app.route('/logout')
def logout():
    """Logout by removing session keys and all tokens from database"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    tokens = Token.query.filter_by(user=user).all()
    for token in tokens:
        db.session.delete(token)
    db.session.commit()
    session.pop('user_id', None)
    session.pop('twitter_id', None)
    session.pop('twitter_name', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run()
