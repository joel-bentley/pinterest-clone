import os
from flask import Flask, redirect, render_template, request, url_for

# from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

# toolbar = DebugToolbarExtension(app)


@app.route('/')
def index():
    user = None
    return render_template('home.html',
                           app_name='Pinterest Clone',
                           title='All images',
                           user=user
                           )



if __name__ == '__main__':
    app.run()
