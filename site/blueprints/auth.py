# auth.py - Routing blueprint for /auth (authentication)
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

import time
import re

from flask import Blueprint, render_template, redirect, url_for, flash, session, make_response, current_app

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

import db
from extensions import limiter

bp = Blueprint('auth', __name__, url_prefix='/auth')
ph = PasswordHasher()

# Password validation
# Policy: 12-24 chars 1 lower, 1 upper, 1 digit, 1 symbol; >24 chars valid no matter what
def validate_password_policy(password):
    if len(password) < 12:
        return False

    if len(password) > 24:
        return True

    has_upper = re.search(r"[A-Z]", password)
    has_lower = re.search(r"[a-z]", password)
    has_digit = re.search(r"\d", password)
    has_symbol = re.search(r"[!@#$%^&*()\[\]_\-+=,.?<>~|/\\{}]", password)

    return all([has_upper, has_lower, has_digit, has_symbol])

# Forms
class RegisterForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=1, max=50)])
    email = StringField('email', validators=[Length(max=100)]) # optional
    password = PasswordField('password', validators=[DataRequired(), Length(min=12)])
    confirm = PasswordField('confirm password', validators=[DataRequired(), EqualTo('password', message='password mismatch')])
    submit = SubmitField('request account')

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('login')

# Routes
@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if 'username' in session:
        return redirect(url_for('social.announce'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user_auth = db.fetch_user_auth(username)

        if user_auth:
            try:
                if ph.verify(user_auth['password_hash'], password):
                    # check user account status
                    if user_auth['status'] != 'active':
                        flash(f"account status: {user_auth['status']}")
                        return render_template('login.html', title='login', form=form)

                    session['username'] = username
                    session['uid'] = user_auth['id']
                    session['role'] = user_auth['role']
                    return redirect(url_for('social.announce'))
            except VerifyMismatchError:
                pass
        else:
            try:
                dummy_hash = '$argon2id$v=19$m=65536,t=3,p=4$ATQxgMcSIpT2cnBXT5jsSw$2Q9QgrVg2ym6jdS9IQjKSdLacqICyG4Y01TFn0ekrhg'
                ph.verify(dummy_hash, "invalid_password")
            except VerifyMismatchError:
                pass

        flash('login failed')

    response = make_response(render_template('login.html', title='login', form=form))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per hour")
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        if not validate_password_policy(form.password.data):
            flash('password must meet minimum requirements')
            return render_template('register.html', title='register', form=form)

        hashed_pw = ph.hash(form.password.data)

        try:
            conn = db.get_connection('login_bot')
            db.execute_query(conn, "CALL sp_register_user(%s, %s, %s)",
                            (form.username.data, hashed_pw, form.email.data),
                            commit=True)
            conn.close()

            flash('account request submitted.')
            return redirect(url_for('auth.login'))

        except Exception as e:
            if "Duplicate entry" in str(e):
                flash('username in use.')
            else:
                flash('registration failed.')
                print(f"Reg Error: {e}")

    return render_template('register.html', title='register', form=form)
