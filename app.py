import os
from flask import Flask, redirect, render_template, request, url_for

# from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

# toolbar = DebugToolbarExtension(app)

images = [
    {'text': 'Here is a cat', 'image': 'https://placekitten.com/g/180/150'}
    for __ in range(10)
]

app_name = 'Pinterest Clone'
user = 'User'


@app.route('/')
def home():
    return render_template('home.html',
                           title='All images',
                           app_name=app_name,
                           images=images,
                           user=user
                           )


@app.route('/myimages/')
def my_images():
    return render_template('home.html',
                           title='My images',
                           app_name=app_name,
                           images=images[0:2],
                           user=user
                           )


@app.route('/login/')
def login():
    return 'login'


@app.route('/logout/')
def logout():
    return 'logout'


if __name__ == '__main__':
    app.run()
