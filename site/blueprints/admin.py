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

# admin.py - Routing blueprint for /admin (administration)
# Copyright (C) 2026 Aaron Reichenbach

import secrets
import string
import math

from flask import Blueprint, render_template, flash, redirect, url_for, request, session
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
    
    # State dictionary for URL generation
    current_state = {'page': page, 'sort': sort_col, 'dir': sort_dir}

    # Validation
    valid_cols = ['id', 'username', 'role', 'status']
    if sort_col not in valid_cols: sort_col = 'id'
    if sort_dir not in ['asc', 'desc']: sort_dir = 'desc'

    per_page = 25
    offset = (page - 1) * per_page
    
    # Fetch Data
    raw_users = db.fetch_all_users(per_page, offset, sort_col, sort_dir)
    
    # Process Data for Table Component
    table_rows = []
    for user in raw_users:
        row = {
            'id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'status': user['status'],
            'actions': []
        }
        
        # Logic: Determine Actions based on Status
        if user['status'] == 'requested':
            row['actions'] = [
                {
                    'label': 'Approve',
                    'icon': '&#10004;', # Checkmark
                    # ADDED: **current_state to pass page/sort params
                    'href': url_for('admin.approve', user_id=user['id'], **current_state),
                    'method': 'POST',
                    'class': 'text-success'
                },
                {
                    'label': 'Deny',
                    'icon': '&#10006;', # X
                    # ADDED: **current_state
                    'href': url_for('admin.deny', user_id=user['id'], **current_state),
                    'method': 'POST',
                    'class': 'destructive',
                    'confirm': f"Deny request for {user['username']}?"
                }
            ]
        else:
            row['actions'] = [
                {
                    'label': 'Details',
                    'icon': '&#8505;', # i
                    # ADDED: **current_state
                    'href': url_for('admin.users', selected_user_id=user['id'], **current_state),
                    'method': 'GET',
                    'class': ''
                }
            ]
        
        table_rows.append(row)

    # Column Definition with Sort Logic
    base_columns = [
        {'key': 'id', 'label': 'ID'},
        {'key': 'username', 'label': 'Username'},
        {'key': 'role', 'label': 'Role'},
        {'key': 'status', 'label': 'Status'}
    ]

    columns = []
    for col in base_columns:
        next_dir = 'desc'
        label = col['label']

        if col['key'] == sort_col:
            next_dir = 'asc' if sort_dir == 'desc' else 'desc'
            label += ' ▼' if sort_dir == 'desc' else ' ▲'
        
        columns.append({
            'key': col['key'],
            'label': label,
            'sort_href': url_for('admin.users', page=1, sort=col['key'], dir=next_dir)
        })

    # Modal Logic
    modal_data = None
    if selected_user_id:
        user_details = db.fetch_user_details(selected_user_id)
        if user_details:
            modal_data = {
                'title': f"User: {user_details['username']}",
                'close_href': url_for('admin.users', page=page, sort=sort_col, dir=sort_dir),
                'details': [
                    {'key': 'ID', 'value': user_details['id']},
                    {'key': 'Email', 'value': user_details['email']},
                    {'key': 'Role', 'value': user_details['role']},
                    {'key': 'Status', 'value': user_details['status']},
                    {'key': 'Created', 'value': user_details['created_at']},
                    {'key': 'Suspended Until', 'value': user_details['suspended_until'] if user_details['suspended_until'] else 'N/A'}
                ],
                'user': user_details
            }

    # Pagination Logic
    total_records = 0
    if raw_users:
        total_records = raw_users[0]['total_records']
    
    total_pages = math.ceil(total_records / per_page) if per_page > 0 else 1
    
    pagination = {
        'page': page,
        'has_next': page < total_pages,
        'has_prev': page > 1,
        'next_href': url_for('admin.users', page=page + 1, sort=sort_col, dir=sort_dir),
        'prev_href': url_for('admin.users', page=page - 1, sort=sort_col, dir=sort_dir),
        'pages': total_pages,
        'total_records': total_records,
        # ADDED: Passing sort state to template so Modal actions can use it
        'sort': sort_col,
        'dir': sort_dir
    }

    return render_template(
        'admin_users.html', 
        title='users',
        columns=columns,
        rows=table_rows,
        modal_data=modal_data,
        pagination=pagination
    )

# --- Helper to extract state from request ---
def get_state():
    return {
        'page': request.args.get('page', 1, type=int),
        'sort': request.args.get('sort', 'id'),
        'dir': request.args.get('dir', 'desc')
    }

@admin_bp.route('/users/approve/<int:user_id>', methods=['POST'])
def approve(user_id):
    try:
        db.approve_user(user_id)
        flash(f"UID {user_id} Approved")
    except Exception as e:
        flash(f"Approval error: {e}")
    return redirect(url_for('admin.users', **get_state()))

@admin_bp.route('/users/deny/<int:user_id>', methods=['POST'])
def deny(user_id):
    try:
        db.deny_user(user_id)
        flash(f"UID {user_id} Denied")
    except Exception as e:
        flash(f"Denial error: {e}")
    return redirect(url_for('admin.users', **get_state()))

@admin_bp.route('/users/suspend/<int:user_id>/<int:duration>', methods=['POST'])
def suspend_user(user_id, duration):
    try:
        db.suspend_user(user_id, duration)
        flash(f"User {user_id} suspended for {duration}h.")
    except Exception as e:
        flash(f"Error suspending: {e}")
    # Maintain selection on suspend
    return redirect(url_for('admin.users', selected_user_id=user_id, **get_state()))

@admin_bp.route('/users/ban/<int:user_id>', methods=['POST'])
def ban_user(user_id):
    try:
        db.ban_user(user_id)
        flash(f"User {user_id} BANNED.")
    except Exception as e:
        flash(f"Error banning: {e}")
    return redirect(url_for('admin.users', selected_user_id=user_id, **get_state()))

@admin_bp.route('/users/reinstate/<int:user_id>', methods=['POST'])
def reinstate_user(user_id):
    try:
        db.reinstate_user(user_id)
        flash(f"User {user_id} reinstated.")
    except Exception as e:
        flash(f"Error reinstating: {e}")
    return redirect(url_for('admin.users', selected_user_id=user_id, **get_state()))

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    try:
        db.delete_user(user_id)
        flash(f"User {user_id} DELETED.")
        # Don't maintain selection (user is gone), but maintain page state
        return redirect(url_for('admin.users', **get_state())) 
    except Exception as e:
        flash(f"Error deleting: {e}")
        return redirect(url_for('admin.users', selected_user_id=user_id, **get_state()))

@admin_bp.route('/users/reset_pass/<int:user_id>', methods=['POST'])
def reset_pass(user_id):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    new_pass = ''.join(secrets.choice(alphabet) for i in range(16))
    try:
        hashed_pw = ph.hash(new_pass)
        db.reset_password(user_id, hashed_pw)
        flash(f"Password reset for User {user_id}. New Password: {new_pass}")
    except Exception as e:
        flash(f"Error resetting password: {e}")
    return redirect(url_for('admin.users', selected_user_id=user_id, **get_state()))

# ... (Announcements route placeholder) ...
@admin_bp.route('/announce', methods=['GET', 'POST'])
def announce():
    return render_template('admin.html', title='announce')