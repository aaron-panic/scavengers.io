# social.py - Routing blueprint for /social ('social'+)
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
    redirect,
    url_for,
    flash,
    session,
    make_response
)

import db.announcements
from middleware import check_access
from utils import format_post

from components.widgets import WidgetText
from components.containers import ContainerPanel, ContainerStack
from factory import build_page

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

bp = Blueprint('social', __name__, url_prefix='/social')



# -----------------------------------------------------------------------------
# Scene Building
# -----------------------------------------------------------------------------

def _build_announcement_scene(posts):
    content = []

    if not posts:
        msg = WidgetText('currently no announcements.')

        panel = ContainerPanel(
            title = 'no announcements',
            children = [msg]
        )

        content.append(panel)
    
    else:
        for i, post in enumerate(posts):
            start_collapsed = (i > 0)
            
            body = WidgetText(content=post.get('content', ''))
            
            panel = ContainerPanel(
                title=post.get('title', 'Untitled'),
                subtitle=post.get('subtitle'),
                author=post.get('username', 'Unknown'),
                timestamp=post.get('created_at'),
                footnote=post.get('footnote'),
                collapsible=True,
                start_collapsed=start_collapsed,
                children=[body]
            )
            
            content.append(panel)
    
    stack = ContainerStack(
        gap="medium",
        children=content
    )

    return build_page(content=[stack], title="announcements")


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------

@bp.app_template_filter('format_post')
def format_post_filter(text):
    return format_post(text)


@bp.before_request
def restrict_access():
    """
    Enforce login requirements for all routes in this blueprint.
    """
    return check_access(['admin', 'user', 'social'])

@bp.route('/announcements')
def announcements():
    """
    Display the latest administrator announcements
    """
    posts = db.announcements.fetch_announcements()
    page = _build_announcement_scene(posts)

    return make_response(render_template(page.template, this = page))

# -----------------------------------------------------------------------------

@bp.route('/feed')
def feed():
    """
    User's personal activity feed.
    """
    return render_template('offline.html', title='feed')

# -----------------------------------------------------------------------------

@bp.route('/chat')
def chat():
    """
    Real-time chat interface.
    """
    return render_template('offline.html', title='chat')

# -----------------------------------------------------------------------------

@bp.route('/profile')
def profile():
    """
    User profile management.
    """
    return render_template('offline.html', title='profile')