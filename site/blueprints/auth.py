# auth.py - Routing blueprint for / (authentication)
# Copyright (C) 2026 Aaron Reichenbach
#
# This program is free software: you can redistribute it and/or modify         
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

 # This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from flask import (
    Blueprint,
    render_template,
    redirect, url_for,
    flash,
    session,
    make_response,
    current_app
)

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Email

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from mysql.connector import Error as DBError

import db.core as db
from extensions import limiter
from config import DUMMY_HASH, USER_DETAIL_LIMITS, PASSWORD_POLICY
from utils import validate_password



# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

bp = Blueprint('auth', __name__)
ph = PasswordHasher()



# -----------------------------------------------------------------------------
# Forms
# -----------------------------------------------------------------------------

class RegisterForm(FlaskForm):
    """
    Form for new user registration.
    Requires username, password. Email is optional.
    """

    username = StringField('username', validators=[
        DataRequired(),
        Length(
            min = USER_DETAIL_LIMITS['username-min-length'],
            max = USER_DETAIL_LIMITS['username-max-length']
        )
    ])

    email = StringField('email', validators=[
        Length(max = USER_DETAIL_LIMITS['email-max-length']),
        Email()
    ])

    password = PasswordField('password', validators=[
        DataRequired(),
        Length(
            min = PASSWORD_POLICY['min-length'],
            max = PASSWORD_POLICY['max-length']
        )
    ])

    confirm = PasswordField('confirm password', validators=[
        DataRequired(),
        EqualTo('password', message='password mismatch')
    ])
    
    submit = SubmitField('request account')

# -----------------------------------------------------------------------------

class LoginForm(FlaskForm):
    """
    Form for user authentication.
    """

    username = StringField('username', validators=[
        DataRequired()
    ])

    password = PasswordField('password', validators=[
        DataRequired()
    ])

    submit = SubmitField('login')


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

def _check_account_status(user_data: dict) -> bool:
    """
    Verify if the user's account status allows for login.
    
    :param user_data: Dictionary containing user row from DB.
    :return: True if allowed, False (and flashes message) if denied.
    """

    status = user_data.get('status')
    
    match status:
        case 'active':
            return True
        case 'requested':
            flash('account pending admin approval.')
        case 'suspended':
            until = user_data.get('suspended_until', 'unknown')
            flash(f'account suspened until: {until}.')
        case 'banned':
            flash('account banned.')
    
    return False

# -----------------------------------------------------------------------------

def _register_user_db(username: str, password_hash: str, email: str) -> bool:
    """
    Execute the stored procedure to create a user request.
    
    :return: True if successful, False if username exists/error.
    """
    conn = None
    try:
        # login role is used for both login and registration request
        conn = db.get_connection('login')
        
        db.execute_procedure(
            conn, 
            'sp_create_user_request', 
            (username, password_hash, email), 
            commit=True
        )

        return True
        
    except DBError as e:

        # on the fence if exposing that a username is already in use to user is
        # necessary. On one hand, it confirms to an attacker that a username 
        # exists. On the other, it creates user frustration if they can't 
        # register and no reason is given. Leaving it as default security-first
        # for now. Maybe I'll have a change of heart later.
        if "Duplicate entry" in str(e):
            return False
        
        # log all other errors locally.
        print(f"Registration Error: {e}")
        return False
    
    finally:
        if conn and conn.is_connected():
            conn.close()



# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------

@bp.route('/')
def start():
    """
    Redirects to the announcements page if logged in, otherwise forces login
    """

    if 'user_id' in session:
        return redirect(url_for('social.announcements'))
    return redirect(url_for('auth.login'))

# -----------------------------------------------------------------------------

@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    """
    Handle user login.
    """

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user_data = None
        target_hash = DUMMY_HASH
        user_found = False

        # fetch user
        try:
            conn = db.get_connection('login')
            rows = db.execute_procedure(conn, 'sp_fetch_user_auth', (username,))
            
            if rows:
                user_data = rows[0]
                # overwrite DUMMY_HASH for verification
                target_hash = user_data['password_hash']
                user_found = True
                
        except DBError as e:
            print(f'Database errror: {e}')
        finally:
            if conn and conn.is_connected():
                conn.close()

        # this always executes to try and mitigate timing attacks
        try:
            ph.verify(target_hash, password)
            password_valid = True
        except VerifyMismatchError:
            password_valid = False

        # actually log in and set up session here
        if user_found and password_valid:
            if _check_account_status(user_data):
                # Set Session
                session.clear()
                session['user_id'] = user_data['id']
                session['username'] = user_data['username']
                session['role'] = user_data['role']
                
                return redirect(url_for('social.announcements'))
        else:
            flash('login failed.')

    # headers to prevent caching of the login page
    response = make_response(render_template('login.html', title='login', form=form))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response

# -----------------------------------------------------------------------------

@bp.route('/logout')
def logout():
    """
    Clear session and redirect to login.
    """

    session.clear()
    return redirect(url_for('auth.login'))

# -----------------------------------------------------------------------------

@bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per hour")
def register():
    """
    Handle new user registration requests.
    """

    form = RegisterForm()

    if form.validate_on_submit():
        
        # validation
        if not validate_password(form.password.data):
            flash('password does not meet security requirements.')
            return render_template('register.html', title='register', form=form)

        hashed_pw = ph.hash(form.password.data)

        # attempt db insertion
        success = _register_user_db(
            form.username.data, 
            hashed_pw, 
            form.email.data
        )

        if success:
            flash('account request submitted.')
            return redirect(url_for('auth.login'))
        else:
            # vague on purpose
            flash('username unavailable or registration failed.')

    return render_template('register.html', title='register', form=form)