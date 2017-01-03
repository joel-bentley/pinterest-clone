import os
from flask import Flask, redirect, render_template, request, url_for, session
from flask_oauthlib.client import OAuth

# from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

oauth = OAuth()
twitter = oauth.remote_app('twitter',
                           base_url='https://api.twitter.com/1/',
                           request_token_url='https://api.twitter.com/oauth/request_token',
                           access_token_url='https://api.twitter.com/oauth/access_token',
                           authorize_url='https://api.twitter.com/oauth/authenticate',
                           consumer_key=os.environ['TWITTER_KEY'],
                           consumer_secret=os.environ['TWITTER_SECRET']
                           )

# toolbar = DebugToolbarExtension(app)

images = [
    {'text': 'Here is a cat', 'image': 'https://placekitten.com/g/180/150'}
    for __ in range(10)
]

app_name = 'Pinterest Clone'


@app.route('/')
def home():
    try:
        user = session['twitter_user']
    except Exception:
        user = None
    return render_template('home.html',
                           title='All images',
                           app_name=app_name,
                           images=images,
                           user=user
                           )


@app.route('/myimages')
def my_images():
    try:
        user = session['twitter_user']
    except Exception:
        user = None
    return render_template('home.html',
                           title='My images',
                           app_name=app_name,
                           images=images[0:2],
                           user=user
                           )


@app.route('/login')
def login():
    return render_template('login.html',
                           title='Login',
                           app_name=app_name
                           )


@twitter.tokengetter
def get_twitter_token(token=None):
    return session.get('twitter_token')


@app.route('/auth/twitter')
def twitter_auth():
    return twitter.authorize(callback=url_for('twitter_auth_callback'))


@app.route('/auth/twitter/callback')
def twitter_auth_callback():
    next_url = url_for('home')
    resp = twitter.authorized_response()
    if resp is None:
        return redirect(next_url)

    session['twitter_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )
    session['twitter_user'] = resp['screen_name']

    return redirect(next_url)


@app.route('/logout')
def logout():
    session.pop('twitter_user', None)
    return redirect(request.referrer or url_for('home'))


if __name__ == '__main__':
    app.run()
