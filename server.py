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

    #debugging prints 
    #app.logger.info(request.form)
    #app.logger.info(db.session.query(User).filter(User.email == email_address).all())

    # to check if the filtered query exists in the users table  
    if db.session.query(User).filter(User.email == email_address).all():
        message = "Email address already registered to an existing user. Please log in."
     
        # debugging to print the message in the debugger log  
        #app.logger.info(str(message))
        flash(message)
        return render_template("log_in.html")
    else:
        #adding the new user to the database 
        new_user = User(email = email_address, password = password, age = age, zipcode = zip_code)

        #debugging print 
        #app.logger.info(str(new_user))

        #commiting the new user to the database 
        db.session.add(new_user)
        db.session.commit()

    return redirect("/")

@app.route('/log_in')
def log_in_form():
    """render the log in page"""

    return render_template("log_in.html")

@app.route('/log_in',methods=["POST"])
def log_in_process():
    """ handle log in with the post data from log_in html"""

    email_address = request.form.get('email')
    password = request.form.get('password')

    user = db.session.query(User).filter(User.email == email_address).one()
    if user.password == password:
        session['current_user_id'] = user.user_id
        flash (' logged in as {}'.format(email_address))

        return redirect(f"/users/{user.id}")
    else:
        flash("wrong password, try again")
        return redirect('/log_in')

@app.route('/log_out', methods=["POST"])
def log_out():
    """ handeling log out """
    if session:
        session.clear() 
        flash("your are logged out")

    return redirect("/")

@app.route("/users/<user_id>")
def show_user_profile(user_id):
    """show the user detail for the specific user id"""

    user = db.session.query(User).filter(User.user_id == user_id).first()
    zipcode = user.zipcode
    age = user.age 

    movie_rating_info = db.session.query(Rating.movie_id, Movie.title,
        Rating.movie_score).join(Movie).filter(Rating.user_id== user_id).all()

    #debugging 
    app.logger.info(str(movie_rating_info))

    return render_template("user.html", zipcode=zipcode, age= age,
        user= user, movie_rating_info=movie_rating_info)

@app.route('/movies')
def movie_list():
    """show list of movies"""

    movies= Movie.query.order_by(Movie.title).all()
    return render_template("movie_list.html", movies=movies)


@app.route("/movies/<movie_title>")
def movie_detail_page(movie_title):
    """show the user detail for the specific user id"""

    movie= db.session.query(Movie).filter(Movie.title == movie_title).first()



    movie_score_list = db.session.query(Rating.movie_score).join(Movie).filter(Movie.title== movie_title).all()

    app.logger.info(str(movie_score_list))
 
    

    return render_template("movie.html", movie_score_list=movie_score_list, movie=movie)


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
