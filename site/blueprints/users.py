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
    session,
    make_response
)
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, Optional

import db.tickets
from middleware import check_access
from utils import flash_form_errors, get_pagination_metadata

from components.widgets import WidgetText, WidgetForm, WidgetButton
from components.containers import ContainerPanel, ContainerStack
from factory import build_page


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

bp = Blueprint('users', __name__, url_prefix='/users')

REQUEST_STATUS_CHOICES = [
    ('', 'all statuses'),
    ('Pending', 'pending'),
    ('In_Progress', 'in progress'),
    ('Completed', 'completed'),
    ('Rejected', 'rejected')
]

PER_PAGE = 10


# -----------------------------------------------------------------------------
# Forms
# -----------------------------------------------------------------------------

class ReportForm(FlaskForm):
    target = StringField('Target', validators=[
        DataRequired(message='Target is required (e.g., User Name, Post Title).'),
        Length(max=255, message='Target must be less than 255 characters.')
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(message='Description is required.')
    ])


class RequestForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(message='Title is required.'),
        Length(max=255, message='Title must be less than 255 characters.')
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(message='Description is required.')
    ])


class RequestFilterForm(FlaskForm):
    tag = SelectField('tag', choices=[('', 'all tags')], validators=[Optional()])
    status = SelectField('status', choices=REQUEST_STATUS_CHOICES, validators=[Optional()])
    my_requests = BooleanField('my requests only')


# -----------------------------------------------------------------------------
# Scene Building
# -----------------------------------------------------------------------------

def _build_ticket_panel(ticket, status_messages):
    content = [
        WidgetText(content=ticket.get('description', ''), style='body')
    ]

    if status_messages:
        content.append(WidgetText(content='status history:', style='subtitle'))
        for msg in status_messages:
            status_line = (
                f"[{msg.get('created_at', '')}] "
                f"{msg.get('old_status', '')} -> {msg.get('new_status', '')}: "
                f"{msg.get('status_message', '')}"
            )
            content.append(WidgetText(content=status_line, style='meta'))
    else:
        content.append(WidgetText(content='No status messages yet.', style='meta'))

    return ContainerPanel(
        title=ticket.get('title', 'untitled request'),
        author=ticket.get('username', 'unknown'),
        timestamp=ticket.get('created_at'),
        footnote=ticket.get('status', 'pending'),
        collapsible=True,
        collapse_footer=False,
        children=content
    )


def _build_requests_scene(request_form, filter_form, tickets, pagination, tag_rows):
    form_widget = WidgetForm(
        form=request_form,
        buttons=[],
        action=url_for('users.requests'),
        method='POST',
        render_actions=False,
        form_id='new-request-form'
    )

    submit_button = WidgetButton(
        label='submit request',
        button_type='submit',
        style='primary',
        attrs=' form="new-request-form"'
    )
    clear_button = WidgetButton(
        label='clear',
        button_type='reset',
        style='secondary',
        attrs=' form="new-request-form"'
    )

    top_panel = ContainerPanel(
        title='new request',
        children=[form_widget],
        footer=ContainerStack(
            gap='small',
            **{'class': ' wid-con-stack-row wid-con-stack-end'},
            children=[submit_button, clear_button]
        )
    )

    ticket_panels = []
    if tickets:
        for i, ticket in enumerate(tickets):
            status_messages = db.tickets.fetch_ticket_status_messages(ticket['id'])
            panel = _build_ticket_panel(ticket, status_messages)
            panel.start_collapsed = (i > 0)
            ticket_panels.append(panel)
    else:
        ticket_panels.append(
            ContainerPanel(
                title='no requests',
                children=[WidgetText(content='No requests match the current filters.')]
            )
        )

    tag_buttons = []
    for tag in tag_rows:
        tag_name = tag.get('name', '')
        if not tag_name:
            continue

        href = url_for(
            'users.requests',
            page=1,
            status=filter_form.status.data or '',
            tag=tag_name,
            my_requests='1' if filter_form.my_requests.data else ''
        )
        style = 'primary' if (filter_form.tag.data == tag_name) else 'secondary'
        tag_buttons.append(WidgetButton(label=tag_name, href=href, style=style))

    all_tags_href = url_for(
        'users.requests',
        page=1,
        status=filter_form.status.data or '',
        tag='',
        my_requests='1' if filter_form.my_requests.data else ''
    )
    tag_buttons.insert(
        0,
        WidgetButton(
            label='all tags',
            href=all_tags_href,
            style='primary' if not filter_form.tag.data else 'secondary'
        )
    )

    status_buttons = []
    for status_value, status_label in REQUEST_STATUS_CHOICES:
        href = url_for(
            'users.requests',
            page=1,
            status=status_value,
            tag=filter_form.tag.data or '',
            my_requests='1' if filter_form.my_requests.data else ''
        )
        style = 'primary' if (filter_form.status.data == status_value) else 'secondary'
        status_buttons.append(WidgetButton(label=status_label, href=href, style=style))

    my_requests_href = url_for(
        'users.requests',
        page=1,
        status=filter_form.status.data or '',
        tag=filter_form.tag.data or '',
        my_requests='' if filter_form.my_requests.data else '1'
    )

    filter_content = [
        WidgetText(content='filter by status:', style='subtitle'),
        ContainerStack(
            gap='small',
            **{'class': ' wid-con-stack-row wid-con-stack-wrap'},
            children=status_buttons
        ),
        WidgetText(content='scope:', style='subtitle'),
        WidgetButton(
            label='my requests only' if filter_form.my_requests.data else 'all requests',
            href=my_requests_href,
            style='primary' if filter_form.my_requests.data else 'secondary'
        ),
        WidgetText(content='filter by tag:', style='subtitle'),
        ContainerStack(
            gap='small',
            **{'class': ' wid-con-stack-row wid-con-stack-wrap'},
            children=tag_buttons
        )
    ]

    nav_buttons = [
        WidgetButton(
            label='previous',
            **{'class': ' wid-pagination-prev'},
            href=pagination['prev_href'] if pagination['has_prev'] else None,
            style='secondary',
            attrs='' if pagination['has_prev'] else ' disabled'
        ),
        WidgetText(content=f"page {pagination['page']} of {pagination['pages']}", style='meta', **{'class': ' wid-pagination-center'}),
        WidgetButton(
            label='next',
            **{'class': ' wid-pagination-next'},
            href=pagination['next_href'] if pagination['has_next'] else None,
            style='secondary',
            attrs='' if pagination['has_next'] else ' disabled'
        )
    ]

    filter_panel = ContainerPanel(
        title='filters & pagination',
        collapsible=False,
        children=filter_content,
        footer=ContainerStack(
            gap='small',
            **{'class': ' wid-con-stack-row wid-pagination-bar'},
            children=nav_buttons
        )
    )

    stack = ContainerStack(
        gap='medium',
        children=[top_panel, *ticket_panels, filter_panel]
    )

    return build_page(content=[stack], title='requests')


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------

@bp.before_request
def restrict_access():
    return check_access(['admin', 'user'])


@bp.route('/media')
def media():
    return render_template('offline.html', title='media')


@bp.route('/report', methods=['GET', 'POST'])
def report():
    return redirect(url_for('users.requests'))


@bp.route('/requests', methods=['GET', 'POST'])
def requests():
    request_form = RequestForm()

    if request_form.validate_on_submit():
        try:
            db.tickets.create_ticket(
                u_id=session.get('user_id'),
                ticket_type='request',
                title=request_form.title.data,
                description=request_form.description.data,
                priority=None
            )
            flash('Request submitted successfully.', 'success')
            return redirect(url_for('users.requests'))
        except Exception as e:
            print(f'Request creation error: {e}')
            flash('An error occurred while submitting your request.', 'error')
    elif request.method == 'POST' and request_form.errors:
        flash_form_errors(request_form)

    page = request.args.get('page', 1, type=int)
    page = page if page > 0 else 1
    offset = (page - 1) * PER_PAGE

    filter_form = RequestFilterForm(request.args, meta={'csrf': False})

    tag_rows = db.tickets.fetch_ticket_tag_list()
    filter_form.tag.choices = [('', 'all tags')] + [
        (tag.get('name', ''), tag.get('name', ''))
        for tag in tag_rows if tag.get('name')
    ]

    selected_tag = request.args.get('tag', '')
    selected_status = request.args.get('status', '')
    my_requests = request.args.get('my_requests', '') in ['1', 'true', 'on', 'yes']

    filter_form.tag.data = selected_tag if selected_tag in dict(filter_form.tag.choices) else ''
    filter_form.status.data = selected_status if selected_status in dict(filter_form.status.choices) else ''
    filter_form.my_requests.data = my_requests

    if my_requests:
        rows = db.tickets.fetch_tickets_by_user(
            u_id=session.get('user_id'),
            ticket_type='request',
            status=filter_form.status.data or None,
            tag_name=filter_form.tag.data or None,
            limit=PER_PAGE,
            offset=offset
        )
    else:
        rows = db.tickets.fetch_tickets(
            ticket_type='request',
            status=filter_form.status.data or None,
            tag_name=filter_form.tag.data or None,
            limit=PER_PAGE,
            offset=offset
        )

    total_records = rows[0].get('total_records', 0) if rows else 0

    pagination = get_pagination_metadata(
        page,
        PER_PAGE,
        total_records,
        'users.requests',
        status=filter_form.status.data or '',
        tag=filter_form.tag.data or '',
        my_requests='1' if filter_form.my_requests.data else ''
    )

    page_obj = _build_requests_scene(
        request_form=request_form,
        filter_form=filter_form,
        tickets=rows,
        pagination=pagination,
        tag_rows=tag_rows
    )

    return make_response(render_template(page_obj.template, this=page_obj))


@bp.route('/dev')
def dev():
    return redirect(url_for('users.requests'))


@bp.route('/board')
def board():
    return redirect(url_for('users.requests'))
