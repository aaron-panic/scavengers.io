from flask import Blueprint, render_template, flash, redirect, url_for
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

@admin_bp.route('/users/approve/<int:user_id>', methods=['POST'])
def approve(user_id):
    try:
        db.approve_user(user_id)
        flash(f"UID {user_id} Approved")
    except Exception as e:
        flash(f"Approval error: UID {user_id}: {e}")

    return redirect(url_for('admin.users'))

@admin_bp.route('/users/deny/<int:user_id>', methods=['POST'])
def deny(user_id):
    try:
        db.deny_user(user_id)
        flash(f"UID {user_id} Denied")
    except Exception as e:
        flash(f"Denial error: UID {user_id}: {e}")
    
    return redirect(url_for('admin.users'))