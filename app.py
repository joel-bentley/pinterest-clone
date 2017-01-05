import os
from flask import Flask
from flask import redirect, render_template, request, session, url_for
from flask_oauthlib.client import OAuth
from flask_sqlalchemy import SQLAlchemy

# from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    twitter_id = db.Column(db.String(80), unique=True)
    twitter_name = db.Column(db.String(80), unique=True)

    def __init__(self, twitter_id, twitter_name):
        self.twitter_id = twitter_id
        self.twitter_name = twitter_name

    def __repr__(self):
        return '<User(id={}, twitter_id={}, twitter_name={})>'.format(self.id, self.twitter_id, self.twitter_name)


class Pin(db.Model):
    __tablename__ = 'pins'

    id = db.Column(db.Integer, primary_key=True)
    twitter_name = db.Column(db.String(80))
    text = db.Column(db.String(140))
    image = db.Column(db.String(140))

    def __init__(self, twitter_name, text, image):
        self.twitter_name = twitter_name
        self.text = text
        self.image = image

    def __repr__(self):
        return '<Pin(id={}, twitter_name={})>'.format(self.id, self.twitter_name)

# toolbar = DebugToolbarExtension(app)


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
    return session.get('twitter_token')


app_name = 'Pinterest Clone'

@app.route('/')
def home():
    twitter_name = session.get('twitter_name')
    images = Pin.query.all()
    return render_template('grid.html',
            title='All images', app_name=app_name, images=images, user=twitter_name)


@app.route('/myimages')
def my_images():
    twitter_name = session.get('twitter_name')
    images = Pin.query.filter_by(twitter_name=twitter_name).all()
    return render_template('grid.html',
            title='My images', app_name=app_name, images=images, user=twitter_name)


@app.route('/newimage', methods=['POST'])
def post_image():
    twitter_name = session['twitter_name']
    image_url = request.form.get('image_url')
    image_text = request.form.get('image_text')

    if twitter_name and image_url and image_text:
        new_pin = Pin(twitter_name, image_text, image_url)
        db.session.add(new_pin)
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

    session['twitter_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )
    twitter_name = resp['screen_name']
    twitter_id = resp['user_id']

    session['twitter_name'] = twitter_name
    session['twitter_id'] = twitter_id

    user = User.query.filter_by(twitter_name=twitter_name).first()

    if not user:
        new_user = User(twitter_id, twitter_name)
        db.session.add(new_user)
        db.session.commit()

    return redirect(next_url)


@app.route('/logout')
def logout():
    session.pop('twitter_name', None)
    session.pop('twitter_id', None)
    session.pop('twitter_token', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run()
