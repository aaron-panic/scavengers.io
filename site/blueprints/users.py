# user.py - Routing blueprint for /user (privileged user features)
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

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from middleware import check_access
import db

users_bp = Blueprint('users', __name__, url_prefix='/users')

# ---------------------------------------------------------
# Forms
# ---------------------------------------------------------

class RequestForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(message="Title is required."),
        Length(max=255, message="Title must be less than 255 characters.")
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(message="Description is required.")
    ])
    ref_1 = StringField('Reference 1', validators=[Optional()])
    ref_2 = StringField('Reference 2', validators=[Optional()])
    ref_3 = StringField('Reference 3', validators=[Optional()])
    submit = SubmitField('Submit Request')

# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------

@users_bp.before_request
def restrict_access():
    return check_access(['admin', 'user'])

@users_bp.route('/media')
def media():
    return render_template('media.html', title='media')

@users_bp.route('/requests', methods=['GET', 'POST'])
def requests():
    # 1. Capture State
    tab_sel = request.args.get('tab_sel', 'all')
    page = request.args.get('page', 1, type=int)
    
    # 2. Navigation / Filter Definition
    tabs = [
        {'slug': 'all',         'label': 'all'},
        {'slug': 'pending',     'label': 'pending'},
        {'slug': 'in_progress', 'label': 'in progress'},
        {'slug': 'completed',   'label': 'completed'},
        {'slug': 'rejected',    'label': 'rejected'},
        {'slug': 'my_requests', 'label': 'my requests'},
        {'slug': 'new',         'label': 'new'}
    ]

    filters = []
    for tab in tabs:
        filters.append({
            'label': tab['label'],
            'href': url_for('users.requests', tab_sel=tab['slug']),
            'active': (tab_sel == tab['slug'])
        })

    if status == 'new':
        # --- CREATE MODE ---
        form = RequestForm()
        
        if form.validate_on_submit():
            try:
                u_id = session.get('user_id')
                
                db.create_request(
                    u_id=u_id,
                    title=form.title.data,
                    description=form.description.data,
                    ref_1=form.ref_1.data,
                    ref_2=form.ref_2.data,
                    ref_3=form.ref_3.data
                )
                flash('Request submitted successfully.', 'success')
                return redirect(url_for('user.requests', tab_sel='my_requests'))
            except Exception as e:
                print(f"Error creating request: {e}")
                flash('An error occurred. Please try again.', 'error')

        return render_template(
            'requests.html', 
            title='requests', 
            filters=filters, 
            form=form,
            show_form=True
        )

    raw_requests = []
    per_page = 12
    offset = (page - 1) * per_page

    if tab_sel == 'my_requests':
        raw_requests = db.fetch_requests_by_uid(uid=session.get('user_id'), limit=per_page + 1, offset=offset)
    
    else:
        raw_requests = db.fetch_requests(status=tab_sel, limit=per_page + 1, offset=offset)

    has_next = len(raw_requests) > per_page
    has_prev = page > 1
        
    display_requests = raw_requests[:per_page]
        
    pagination = {
        'page': page,
        'has_next': has_next,
        'has_prev': has_prev,
        'next_href': url_for('user.requests', status=status, page=page + 1) if has_next else '#',
        'prev_href': url_for('user.requests', status=status, page=page - 1) if has_prev else '#',
        'pages': '?' 
    }

    return render_template(
        'requests.html',
        title='requests',
        filters=filters,
        posts=display_requests,
        pagination=pagination,
        show_form=False
    )

@users_bp.route('/report')
def report():
    return render_template('report.html', title='report')

@users_bp.route('/dev')
def dev():
    return render_template('dev.html', title='dev')