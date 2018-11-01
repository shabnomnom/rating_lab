"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")

@app.route('/users')
def user_list():
    """show list of users"""

    users= User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/register', methods=["GET"])
def register_form():

    return render_template("register.html")


@app.route('/register', methods=["POST"])
def register_process():
    email_address = request.form.get('email')
    password = request.form.get('password')
    age = request.form.get('age')
    zip_code = request.form.get('zipcode')
    app.logger.info(request.form)
    app.logger.info(db.session.query(User).filter(User.email == email_address).all())


    # to check if the filtered query exists in the users table  
    if db.session.query(User).filter(User.email == email_address).all():
        message = "Email address already registered to an existing user. Please log in."
        app.logger.info(str(message))
        return redirect("/")
    else:
        #adding the new user to the databaspe 
        new_user = User(email = email_address, password = password, age = age, zipcode = zip_code)
        app.logger.info(str(new_user))
        db.session.add(new_user)
        db.session.commit()

    return redirect("/")

@app.route('/users/<user_id>')
def user_info(user_id):
    user = db.session.query(User).filter(User.user_id == user_id).first()
    zipcode = user.zipcode 
    age = user.age 

    movie_rating_info = db.session.query(Rating.movie_id, Movie.title,
        Rating.movie_score).join(Movie).filter(Rating.user_id== user_id).all()
    
    app.logger.info(str(movie_rating_info))


    return render_template("user_info.html", zipcode=zipcode, age= age,
        user= user, movie_rating_info=movie_rating_info)




if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
