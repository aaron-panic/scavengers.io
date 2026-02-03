# admin.py - Routing blueprint for /admin (administration)
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

import secrets
import string
from flask import Blueprint, render_template, flash, redirect, url_for
from argon2 import PasswordHasher
from middleware import check_access

import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
ph = PasswordHasher()

@admin_bp.before_request
def restrict_access():
    return check_access(['admin'])

@admin_bp.route('/')
def dashboard():
    return render_template('admin.html', title='admin')

@admin_bp.route('/users')
@admin_bp.route('/users/<int:selected_user_id>')
def users(selected_user_id=None):
    user_list = db.fetch_all_users()
    
    selected_user = None
    if selected_user_id:
        selected_user = db.fetch_user_details(selected_user_id)
        if not selected_user:
            flash(f"No Details: UID: {selected_user_id}")
            return redirect(url_for('admin.users'))
        
    return render_template('admin_users.html', title='users', users=user_list, selected_user=selected_user)

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

@admin_bp.route('/users/suspend/<int:user_id>/<int:duration>', methods=['POST'])
def suspend_user(user_id, duration):
    try:
        db.suspend_user(user_id, duration)
        flash(f"User {user_id} suspended for {duration} hours.")
    except Exception as e:
        flash(f"Error suspending user: {e}")
    # Return to the detail view of the same user
    return redirect(url_for('admin.users', selected_user_id=user_id))

@admin_bp.route('/users/ban/<int:user_id>', methods=['POST'])
def ban_user(user_id):
    try:
        db.ban_user(user_id)
        flash(f"User {user_id} BANNED.")
    except Exception as e:
        flash(f"Error banning user: {e}")
    return redirect(url_for('admin.users', selected_user_id=user_id))

@admin_bp.route('/users/reinstate/<int:user_id>', methods=['POST'])
def reinstate_user(user_id):
    try:
        db.reinstate_user(user_id)
        flash(f"User {user_id} reinstated.")
    except Exception as e:
        flash(f"Error reinstating user: {e}")
    return redirect(url_for('admin.users', selected_user_id=user_id))

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    try:
        db.delete_user(user_id)
        flash(f"User {user_id} DELETED.")
        # Return to main list since user is gone
        return redirect(url_for('admin.users')) 
    except Exception as e:
        flash(f"Error deleting user: {e}")
        return redirect(url_for('admin.users', selected_user_id=user_id))

@admin_bp.route('/users/reset_pass/<int:user_id>', methods=['POST'])
def reset_pass(user_id):
    # Generate a secure random 16-char password
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    new_pass = ''.join(secrets.choice(alphabet) for i in range(16))
    
    try:
        hashed_pw = ph.hash(new_pass)
        db.reset_password(user_id, hashed_pw)
        # Must manually copy the password here
        flash(f"Password reset for User {user_id}. New Password: {new_pass}")
    except Exception as e:
        flash(f"Error resetting password: {e}")
        
    return redirect(url_for('admin.users', selected_user_id=user_id))