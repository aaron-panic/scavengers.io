from flask import Blueprint, render_template, redirect, url_for, session
from middleware import check_access

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def start():
    # Redirects to the social feed if logged in, otherwise forces login
    if 'username' in session:
        return redirect(url_for('social.announce'))
    return redirect(url_for('auth.login'))

@home_bp.route('/profile')
def profile():
    access_check = check_access(['admin','user','social'])
    if access_check:
        return access_check
    return render_template('profile.html', title='profile')
