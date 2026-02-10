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
    return render_redirect(url_for('admin.users'))

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

# ---------------------------------------------------------
# Announcements
# ---------------------------------------------------------

@admin_bp.route('/announce', methods=['GET', 'POST'])
def announce():
    # 1. Handle Form Submission (Create / Update)
    if request.method == 'POST':
        # ... (POST logic remains the same) ...
        title = request.form.get('title')
        subtitle = request.form.get('subtitle')
        content = request.form.get('content')
        footnote = request.form.get('footnote')
        edit_id = request.form.get('edit_id')
        is_visible = 1 if 'is_visible' in request.form else 0

        if not title or not content:
            flash("Error: Title and Content are required.")
        else:
            try:
                if edit_id:
                    db.update_announcement(edit_id, title, subtitle, content, footnote, is_visible)
                    flash(f"Announcement '{title}' updated.")
                else:
                    db.create_announcement(session['uid'], title, subtitle, content, footnote, is_visible)
                    flash(f"Announcement '{title}' published.")
            except Exception as e:
                flash(f"Error saving announcement: {e}")
        
        return redirect(url_for('admin.announce'))

    # 2. View / Edit State Setup
    page = request.args.get('page', 1, type=int)
    sort_col = request.args.get('sort', 'created_at') # Default sort by date
    sort_dir = request.args.get('dir', 'desc')
    edit_id = request.args.get('edit_id')
    
    # Validation
    valid_cols = ['id', 'title', 'username', 'created_at']
    if sort_col not in valid_cols: sort_col = 'created_at'
    if sort_dir not in ['asc', 'desc']: sort_dir = 'desc'

    # Fetch Data for Edit Form
    edit_data = None
    if edit_id:
        edit_data = db.get_announcement(edit_id)
        if not edit_data:
            flash(f"Error: Could not fetch post ID {edit_id}")

    # 3. Fetch Data for List
    per_page = 25
    offset = (page - 1) * per_page
    # Pass sort params to DB
    posts = db.list_announcements_admin(per_page, offset, sort_col, sort_dir)
    
    # 4. Prepare Table Data
    table_rows = []
    for post in posts:
        display_title = post['title']
        if len(display_title) > 25:
            display_title = display_title[:25] + "..."

        table_rows.append({
            'id': post['id'],
            'title': display_title,
            'username': post['username'],
            'created_at': post['created_at'],
            'actions': [
                {
                    'label': 'Edit',
                    'icon': '&#8505;', 
                    'href': url_for('admin.announce', edit_id=post['id'], page=page, sort=sort_col, dir=sort_dir),
                    'method': 'GET',
                    'class': ''
                },
                {
                    'label': 'Delete',
                    'icon': '&#10006;', 
                    'href': url_for('admin.delete_announce', post_id=post['id']),
                    'method': 'POST',
                    'class': 'destructive',
                    'confirm': f"Delete announcement '{post['title']}'?"
                }
            ]
        })

    # 5. Build Columns with Sort Links
    base_columns = [
        {'key': 'id', 'label': 'ID'},
        {'key': 'created_at', 'label': 'Date'},
        {'key': 'title', 'label': 'Title'},
        {'key': 'username', 'label': 'Author'}
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
            'sort_href': url_for('admin.announce', page=1, sort=col['key'], dir=next_dir)
        })

    # Pagination Logic
    total_records = 0
    if posts:
        total_records = posts[0]['total_records']
    total_pages = math.ceil(total_records / per_page) if total_records > 0 else 1

    pagination = {
        'page': page,
        'has_next': page < total_pages,
        'has_prev': page > 1,
        'next_href': url_for('admin.announce', page=page + 1, sort=sort_col, dir=sort_dir),
        'prev_href': url_for('admin.announce', page=page - 1, sort=sort_col, dir=sort_dir),
        'pages': total_pages,
        'total_records': total_records
    }

    return render_template(
        'admin_announce.html',
        title='announcements',
        edit_data=edit_data,
        columns=columns,
        rows=table_rows,
        pagination=pagination
    )

@admin_bp.route('/announce/delete/<int:post_id>', methods=['POST'])
def delete_announce(post_id):
    try:
        db.delete_announcement(post_id)
        flash(f"Announcement deleted.")
    except Exception as e:
        flash(f"Error deleting: {e}")
    return redirect(url_for('admin.announce'))

# ---------------------------------------------------------
# Requests Management
# ---------------------------------------------------------

@admin_bp.route('/requests', methods=['GET', 'POST'])
def requests_list():
    # 1. State Management
    page = request.args.get('page', 1, type=int)

    sort_col = request.args.get('sort', 'created_at')
    sort_dir = request.args.get('dir', 'desc')
    edit_id = request.args.get('edit_id')

    # Validation
    valid_cols = ['id', 'title', 'username', 'created_at', 'status']
    if sort_col not in valid_cols: sort_col = 'created_at'
    if sort_dir not in ['asc', 'desc']: sort_dir = 'desc'

    # 2. Fetch Modal Data (if editing)
    modal_data = None
    if edit_id:
        req = db.get_request(edit_id)
        if req:
            modal_data = {
                'title': f"Request #{req['id']}",
                'close_href': url_for('admin.requests_list', page=page, sort=sort_col, dir=sort_dir),
                'details': [
                    {'key': 'Title', 'value': req['title']},
                    {'key': 'User', 'value': req['username']},
                    {'key': 'Created', 'value': req['created_at']},
                    {'key': 'Status', 'value': req['status']},
                    {'key': 'Status Message', 'value': req['status_message'] if req['status_message'] else '-'},
                    {'key': 'Description', 'value': req['description']},
                    {'key': 'Reference 1', 'value': req['ref_1'] if req['ref_1'] else '-'},
                    {'key': 'Reference 2', 'value': req['ref_2'] if req['ref_2'] else '-'},
                    {'key': 'Reference 3', 'value': req['ref_3'] if req['ref_3'] else '-'}
                ],
                'request': req # Pass full object for form population
            }
        else:
            flash(f"Error: Request ID {edit_id} not found.")

    # 3. Fetch List Data
    per_page = 25
    offset = (page - 1) * per_page
    requests = db.list_requests_admin(per_page, offset, sort_col, sort_dir)

    # 4. Prepare Table Rows
    table_rows = []
    for r in requests:
        table_rows.append({
            'id': r['id'],
            'title': r['title'],
            'username': r['username'],
            'created_at': r['created_at'],
            'status': r['status'],
            'actions': [
                {
                    'label': 'Modify',
                    'icon': '&#8505;', # i
                    'href': url_for('admin.requests_list', edit_id=r['id'], page=page, sort=sort_col, dir=sort_dir),
                    'method': 'GET',
                    'class': ''
                },
                {
                    'label': 'Delete',
                    'icon': '&#10006;', # x
                    'href': url_for('admin.delete_request', request_id=r['id']),
                    'method': 'POST',
                    'class': 'destructive',
                    'confirm': f"Delete request #{r['id']}?"
                }
            ]
        })

    # 5. Build Sortable Columns
    base_columns = [
        {'key': 'id', 'label': 'ID'},
        {'key': 'title', 'label': 'Title'},
        {'key': 'username', 'label': 'User'},
        {'key': 'created_at', 'label': 'Date'},
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
            'sort_href': url_for('admin.requests_list', page=1, sort=col['key'], dir=next_dir)
        })

    # Pagination
    total_records = 0
    if requests:
        total_records = requests[0]['total_records']
    total_pages = math.ceil(total_records / per_page) if total_records > 0 else 1

    pagination = {
        'page': page,
        'has_next': page < total_pages,
        'has_prev': page > 1,
        'next_href': url_for('admin.requests_list', page=page + 1, sort=sort_col, dir=sort_dir),
        'prev_href': url_for('admin.requests_list', page=page - 1, sort=sort_col, dir=sort_dir),
        'pages': total_pages,
        'total_records': total_records,
        'sort': sort_col,
        'dir': sort_dir
    }

    return render_template(
        'admin_requests.html',
        title='requests',
        columns=columns,
        rows=table_rows,
        modal_data=modal_data,
        pagination=pagination
    )

@admin_bp.route('/requests/update/<int:request_id>', methods=['POST'])
def update_request(request_id):
    # Retrieve form data
    new_status = request.form.get('status')
    new_message = request.form.get('status_message')

    # Logic: Convert empty strings to None to trigger SQL COALESCE (No Change)
    if not new_message or new_message.strip() == "":
        new_message = None
    
    # We pass new_status directly. 
    # If the dropdown matches current status, SQL updates to same value (No Change).
    
    try:
        db.update_request(request_id, new_status, new_message)
        flash(f"Request #{request_id} updated.")
    except Exception as e:
        flash(f"Error updating request: {e}")

    # Return to list with state preserved
    return redirect(url_for('admin.requests_list', **get_state()))

@admin_bp.route('/requests/delete/<int:request_id>', methods=['POST'])
def delete_request(request_id):
    try:
        db.delete_request(request_id)
        flash(f"Request #{request_id} deleted.")
    except Exception as e:
        flash(f"Error deleting request: {e}")
    
    return redirect(url_for('admin.requests_list', **get_state()))