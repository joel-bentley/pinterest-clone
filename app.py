import os
from flask import Flask, render_template

from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

toolbar = DebugToolbarExtension(app)


@app.route('/')
def index():
    title = 'Pinterest Clone'
    message = 'Hello, world!'
    return render_template('index.html', title=title, message=message)


if __name__ == '__main__':
    app.run()
