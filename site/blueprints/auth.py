# auth.py - Routing blueprint for / ('login'+)
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
    redirect,
    url_for,
    flash,
    session,
    make_response
)

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Email

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

import db.auth
from extensions import limiter
from config import DUMMY_HASH, USER_DETAIL_LIMITS, PASSWORD_POLICY
from utils import validate_password, flash_form_errors

from components.page import Page
from components.layout import LayoutThreeColumn
from components.containers import ContainerPanel, ContainerStack
from components.widgets import WidgetForm, WidgetButton, WidgetStatCard
from factory import build_page



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
# Scene Building
# -----------------------------------------------------------------------------

def _build_login_scene(form):
    submit_button = WidgetButton(
        label = 'login',
        button_type = 'submit',
        style = 'primary'
    )

    login_widget = WidgetForm(
        form = form,
        buttons = [submit_button]
    )

    login_panel = ContainerPanel(
        title = 'auth.login',
        children = [ContainerStack(
            gap = 'medium',
            children = [login_widget]
        )],
        class_ = 'login-panel'
    )

    return build_page(
        content = [login_panel],
        title = 'login'
    )

def _build_register_scene(form):
    submit_button = WidgetButton(
        label = 'request account',
        button_type = 'submit',
        style = 'primary'
    )

    register_widget = WidgetForm(
        form = form,
        buttons = [submit_button]
    )

    register_panel = ContainerPanel(
        title = 'auth.register',
        children = [ContainerStack(
            gap = 'medium',
            children = [register_widget]
        )],
        class_ = 'register-panel'
    )

    return build_page(
        content = [register_panel],
        title = 'register'
    )

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
        
        target_hash = DUMMY_HASH
        user_found = False

        # fetch user
        user_data = db.auth.fetch_user_auth(username)
        
        if user_data:
            target_hash = user_data['password_hash']
            user_found = True

        # this always executes to try and mitigate timing attacks
        try:
            ph.verify(target_hash, password)
            password_valid = True
        except VerifyMismatchError:
            password_valid = False

        # actually log in and set up session here
        if user_found and password_valid:
            if _check_account_status(user_data):
                # set session
                session.clear()
                session['user_id'] = user_data['id']
                session['username'] = user_data['username']
                session['role'] = user_data['role']
                
                return redirect(url_for('social.announcements'))
        else:
            flash('login failed.')
            
    elif form.errors:
        flash_form_errors(form)

    page = _build_login_scene(form)

    # headers to prevent caching of the login page
    response = make_response(render_template(page.template, this = page))

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
        success = db.auth.create_user_request(
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
            
    elif form.errors:
        flash_form_errors(form)

    page = _build_register_scene(form)

    response = make_response(render_template(page.template, this = page))
    return response