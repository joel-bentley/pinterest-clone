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

    def __repr__(self):
        return '<User(id={}, twitter_id={}, twitter_name={})>'.format(self.id, self.twitter_id, self.twitter_name)


class Pin(db.Model):
    __tablename__ = 'pins'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    text = db.Column(db.String(140))
    image = db.Column(db.String(140))

    def __repr__(self):
        return '<Pin(id={}, user_id={})>'.format(self.id, self.user_id)

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


images = [
    {'text': 'Here is a cat', 'image': 'https://placekitten.com/g/180/150'}
    for __ in range(10)
]

app_name = 'Pinterest Clone'

@app.route('/')
def home():
    user = session.get('twitter_name')
    return render_template('grid.html',
            title='All images', app_name=app_name, images=images, user=user)


@app.route('/myimages')
def my_images():
    user = session.get('twitter_name')
    return render_template('grid.html',
            title='My images', app_name=app_name, images=images[0:2], user=user)


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
    session['twitter_name'] = resp['screen_name']
    session['twitter_id'] = resp['user_id']

    return redirect(next_url)


@app.route('/logout')
def logout():
    session.pop('twitter_name', None)
    session.pop('twitter_id', None)
    session.pop('twitter_token', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run()
