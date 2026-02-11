# users.py - Routing blueprint for /users ('user'+)
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
    request, 
    redirect, 
    url_for, 
    flash, 
    session
)
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

import db.reports
import db.requests
from middleware import check_access
from utils import flash_form_errors, get_pagination_metadata



# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

bp = Blueprint('users', __name__, url_prefix='/users')

# Tab configuration for Requests page
REQUEST_TABS = [
    {'slug': 'all',         'label': 'all'},
    {'slug': 'Pending',     'label': 'pending'},
    {'slug': 'In_Progress', 'label': 'in progress'},
    {'slug': 'Completed',   'label': 'completed'},
    {'slug': 'Rejected',    'label': 'rejected'},
    {'slug': 'my_requests', 'label': 'my requests'},
    {'slug': 'new',         'label': 'new'}
]



# -----------------------------------------------------------------------------
# Forms
# -----------------------------------------------------------------------------

class ReportForm(FlaskForm):
    target = StringField('Target', validators=[
        DataRequired(message="Target is required (e.g., User Name, Post Title)."),
        Length(max=255, message="Target must be less than 255 characters.")
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(message="Description is required.")
    ])
    submit = SubmitField('Submit Report')

# -----------------------------------------------------------------------------

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



# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------

@bp.before_request
def restrict_access():
    return check_access(['admin', 'user'])

# -----------------------------------------------------------------------------

@bp.route('/media')
def media():
    return render_template('offline.html', title='media')

# -----------------------------------------------------------------------------

@bp.route('/report', methods=['GET', 'POST'])
def report():
    form = ReportForm()
    
    if form.validate_on_submit():
        try:
            db.reports.create_report(
                u_id=session.get('user_id'),
                target=form.target.data,
                description=form.description.data
            )
            flash('Report submitted successfully.', 'success')
            return redirect(url_for('users.report'))
            
        except Exception as e:
            print(f"Report Error: {e}")
            flash('An error occurred while submitting report.', 'error')
    
    elif form.errors:
        flash_form_errors(form)

    return render_template('report.html', title='report', form=form)

# -----------------------------------------------------------------------------

@bp.route('/requests', methods=['GET', 'POST'])
def requests():
    
    # parameter extraction
    tab_sel = request.args.get('tab_sel', 'all')
    page = request.args.get('page', 1, type=int)

    # navigation tabs
    filters = []
    for tab in REQUEST_TABS:
        filters.append({
            'label': tab['label'],
            'href': url_for('users.requests', tab_sel=tab['slug']),
            'active': (tab_sel == tab['slug'])
        })
    
    # new request view
    if tab_sel == 'new':
        form = RequestForm()
        
        if form.validate_on_submit():
            try:
                db.requests.create_request(
                    u_id=session.get('user_id'),
                    title=form.title.data,
                    description=form.description.data,
                    ref_1=form.ref_1.data,
                    ref_2=form.ref_2.data,
                    ref_3=form.ref_3.data
                )
                flash('Request submitted successfully.', 'success')
                return redirect(url_for('users.requests', tab_sel='my_requests'))
                
            except Exception as e:
                print(f"Request Creation Error: {e}")
                flash('An error occurred. Please try again.', 'error')
        
        return render_template(
            'requests.html', 
            title='requests', 
            filters=filters, 
            form=form,
            show_form=True
        )

    # list view
    per_page = 12
    offset = (page - 1) * per_page
    
    rows = []
    
    if tab_sel == 'my_requests':
        rows = db.requests.fetch_requests_by_user(session.get('user_id'), per_page, offset)
    else:
        rows = db.requests.fetch_requests_by_status(tab_sel, per_page, offset)
        
    # if data exists, we grab how many records total from the first row
    total_records = rows[0].get('total_records', 0) if rows else 0
    
    # build pagination
    pagination = get_pagination_metadata(
        page, 
        per_page, 
        total_records, 
        'users.requests', 
        tab_sel=tab_sel
    )

    return render_template(
        'requests.html',
        title='requests',
        filters=filters,
        posts=rows,
        pagination=pagination,
        show_form=False
    )

# -----------------------------------------------------------------------------

@bp.route('/dev')
def dev():
    return render_template('offline.html', title='dev')