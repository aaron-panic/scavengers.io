from flask import Blueprint, render_template
from middleware import check_access

import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def restrict_access():
    return check_access(['admin'])

@admin_bp.route('/')
def dashboard():
    return render_template('admin.html', title='admin')

@admin_bp.route('/users')
def users():
    user_list = db.fetch_all_users()
    return render_template('admin_users.html', title='users', users=user_list)
