#pinterest-clone
Built for Pinterest Clone challenge on Free Code Camp.

(Python / Flask / OAuth / PostgreSQL)

**Live Demo:** https://joel-bentley-pinterest-clone.herokuapp.com/

---

User story requirements for this project: (<https://www.freecodecamp.com/challenges/build-a-pinterest-clone>)

1. As an unauthenticated user, I can login with Twitter.

2. As an authenticated user, I can link to images.

3. As an authenticated user, I can delete images that I've linked to.

4. As an authenticated user, I can see a Pinterest-style wall of all the images I've linked to.

5. As an unauthenticated user, I can browse other users' walls of images.

6. As an authenticated user, if I upload an image that is broken, it will be replaced by a placeholder image.

---

To use, first check variables in and run script in `.env` file. Then create virtual environment in project folder.

Create PostgreSQL database with name and location you provided in `.env` file.

Create Twitter app and set `TWITTER_KEY` and `TWITTER_SECRET` environmental variables.

You should also set `SECRET_KEY` environmental variable to random string.

To install dependencies type:  `pip install -r requirements.txt`

Then, to start Flask server type:  `python app.py`
