# user.py - Routing blueprint for /user (privileged user features)
# Copyright (C) 2026 Aaron Reichenbach

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from middleware import check_access
import math
import db

users_bp = Blueprint('users', __name__, url_prefix='/users')

# ---------------------------------------------------------
# Forms
# ---------------------------------------------------------

class ReportForm(FlaskForm):
    target = StringField('Target', validators=[
        DataRequired(message="Target is required (e.g., User Name, Post Title)."),
        Length(max=255, message="Target must be less than 255 characters.")
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(message="Description is required.")
    ])
    submit = SubmitField('Submit Report')

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
    return render_template('offline.html', title='users.media')

@users_bp.route('/report', methods=['GET', 'POST'])
def report():
    form = ReportForm()
    
    if form.validate_on_submit():
        try:
            db.create_report(
                u_id=session.get('uid'),
                target=form.target.data,
                description=form.description.data
            )
            flash('Report submitted successfully.', 'success')
            return redirect(url_for('users.report'))
        except Exception as e:
            print(f"Error submitting report: {e}")
            flash('An error occurred. Please try again.', 'error')

    return render_template('report.html', title='users.report', form=form)
    
@users_bp.route('/requests', methods=['GET', 'POST'])
def requests():
    # 1. Capture State
    tab_sel = request.args.get('tab_sel', 'all')
    page = request.args.get('page', 1, type=int)
    
    # 2. Navigation / Filter Definition
    tabs = [
        {'slug': 'all',         'label': 'all'},
        {'slug': 'Pending',     'label': 'pending'},
        {'slug': 'In_Progress', 'label': 'in progress'},
        {'slug': 'Completed',   'label': 'completed'},
        {'slug': 'Rejected',    'label': 'rejected'},
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
    
    # Create new
    if tab_sel == 'new':
        form = RequestForm()
        
        if form.validate_on_submit():
            try:
                u_id = session.get('uid')
                
                db.create_request(
                    u_id=u_id,
                    title=form.title.data,
                    description=form.description.data,
                    ref_1=form.ref_1.data,
                    ref_2=form.ref_2.data,
                    ref_3=form.ref_3.data
                )
                flash('Request submitted successfully.', 'success')
                return redirect(url_for('users.requests', tab_sel='my_requests'))
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

    # --- LIST MODE ---
    raw_requests = []
    per_page = 12
    offset = (page - 1) * per_page

    # Fetch data based on filter
    # Note: We now fetch exactly 'per_page' because we rely on total_records for pagination logic
    if tab_sel == 'my_requests':
        raw_requests = db.fetch_requests_by_uid(uid=session.get('uid'), limit=per_page, offset=offset)
    else:
        raw_requests = db.fetch_requests_by_status(status=tab_sel, limit=per_page, offset=offset)

    # 3. Calculate Pagination Metrics
    total_records = 0
    if raw_requests:
        # Extract the total count provided by the window function in SQL
        total_records = raw_requests[0]['total_records']

    # Avoid division by zero, default to 1 page if empty
    total_pages = math.ceil(total_records / per_page) if total_records > 0 else 1

    has_next = page < total_pages
    has_prev = page > 1
    
    pagination = {
        'page': page,
        'has_next': has_next,
        'has_prev': has_prev,
        'next_href': url_for('users.requests', tab_sel=tab_sel, page=page + 1) if has_next else '#',
        'prev_href': url_for('users.requests', tab_sel=tab_sel, page=page - 1) if has_prev else '#',
        'pages': total_pages
    }

    return render_template(
        'requests.html',
        title='requests',
        filters=filters,
        posts=raw_requests,
        pagination=pagination,
        show_form=False
    )

@users_bp.route('/dev')
def dev():
    return render_template('offline.html', title='users.dev')