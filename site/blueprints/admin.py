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
from flask import Blueprint, render_template, flash, redirect, url_for, request, session
import math
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

# ---------------------------------------------------------
# User Management
# ---------------------------------------------------------

@admin_bp.route('/users')
@admin_bp.route('/users/<int:selected_user_id>')
def users(selected_user_id=None):
    page = request.args.get('page', 1, type=int)
    sort_col = request.args.get('sort', 'id')
    sort_dir = request.args.get('dir', 'desc')
    
    per_page = 50
    offset = (page - 1) * per_page
    
    user_list = db.fetch_all_users(per_page, offset, sort_col, sort_dir)
    
    total_records = 0
    if user_list:
        total_records = user_list[0]['total_records']
    
    total_pages = math.ceil(total_records / per_page)
    
    selected_user = None
    if selected_user_id:
        selected_user = db.fetch_user_details(selected_user_id)
        if not selected_user:
            flash(f"No Details: UID: {selected_user_id}")
            return redirect(url_for('admin.users', page=page, sort=sort_col, dir=sort_dir))
        
    return render_template(
        'admin_users.html', 
        title='users', 
        users=user_list, 
        selected_user=selected_user,
        pagination={
            'current_page': page,
            'total_pages': total_pages,
            'total_records': total_records,
            'sort_col': sort_col,
            'sort_dir': sort_dir
        }
    )

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

    # ---------------------------------------------------------
# Announcements
# ---------------------------------------------------------

@admin_bp.route('/announce', methods=['GET', 'POST'])
def announce():
    # Handle Create / Update Form Submission
    if request.method == 'POST':
        title = request.form.get('title')
        subtitle = request.form.get('subtitle')
        content = request.form.get('content')
        footnote = request.form.get('footnote')
        edit_id = request.form.get('edit_id')

        if not title or not content:
            flash("Error: Title and Content are required.")
        else:
            try:
                if edit_id:
                    # UPDATE
                    db.update_announcement(edit_id, title, subtitle, content, footnote)
                    flash(f"Announcement '{title}' updated.")
                else:
                    # CREATE
                    # Use session ID for security
                    db.create_announcement(session['uid'], title, subtitle, content, footnote)
                    flash(f"Announcement '{title}' published.")
            except Exception as e:
                flash(f"Error saving announcement: {e}")
        
        return redirect(url_for('admin.announce'))

    # Handle View / Edit State
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    posts = db.list_announcements_admin(per_page, offset)
    
    total_records = 0
    if posts:
        total_records = posts[0]['total_records']
    total_pages = math.ceil(total_records / per_page)

    edit_data = None
    edit_id = request.args.get('edit_id')
    if edit_id:
        edit_data = db.get_announcement(edit_id)
        if not edit_data:
            flash(f"Error: Could not fetch post ID {edit_id}")

    return render_template(
        'admin_announce.html',
        title='announce',
        posts=posts,
        edit_data=edit_data,
        pagination={
            'current_page': page,
            'total_pages': total_pages,
            'total_records': total_records
        }
    )

@admin_bp.route('/announce/delete/<int:post_id>', methods=['POST'])
def delete_announce(post_id):
    try:
        db.delete_announcement(post_id)
        flash(f"Announcement deleted.")
    except Exception as e:
        flash(f"Error deleting: {e}")
    return redirect(url_for('admin.announce'))