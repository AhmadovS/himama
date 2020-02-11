#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
from models import *
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
import os
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)


# Login Manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def home():
    tracker = Tracker.query.filter_by(user_id=current_user.id, end_time=None).first()

    all_logs = Tracker.query.filter_by(user_id=current_user.id).all()
    trackerStartime = None
    if tracker:
        trackerStartime = tracker.start_time.__str__()
    return render_template('pages/placeholder.home.html', userId = current_user.id, trackerStartime=trackerStartime,\
                           timeLogs=all_logs, name=current_user.name)


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@app.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('login')) # if user doesn't exist or password is wrong, reload the page
    login_user(user)
    return redirect('/')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)

@app.route('/register', methods=['POST'])
def register_post():

    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(
        email=email).first()  # if this returns a user, then the email already exists in database

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        return redirect(url_for('register'))

    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect((url_for('login')))


@app.route('/clock-in', methods=['POST'])
@login_required
def clock_in():
    clockInTime = request.form.get('clock_in')
    clockInTime= int(clockInTime)//1000

    clockInTime = datetime.fromtimestamp(clockInTime)
    tracker = Tracker(current_user.id, clockInTime)
    db.session.add(tracker)
    db.session.commit()
    all_logs = Tracker.query.filter_by(user_id=current_user.id).all()

    return jsonify({'data': render_template('layouts/table.html', timeLogs=all_logs)})

@app.route('/clock-out', methods=['POST'])
@login_required
def clock_out():
    clockOutTime = request.form.get('clock_out')
    clockOutTime = int(int(clockOutTime) // 1000)

    clockOutTime = datetime.fromtimestamp(clockOutTime)
    tracker = Tracker.query.filter_by(user_id=current_user.id, end_time=None).first()
    tracker.end_time=clockOutTime
    db.session.merge(tracker)
    db.session.commit()
    return redirect('/')

@app.route('/delete-log', methods=['POST'])
@login_required
def delete_log():
    log_id = request.form.get('log_id')
    if not log_id:
        return
    db.session.query(Tracker).filter(Tracker.id==log_id).delete()
    # time_log = Tracker.query.filter_by(id=log_id).delete()
    db.session.commit()
    return redirect('/')

# Error handlers.
@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()
