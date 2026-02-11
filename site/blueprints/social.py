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
    current_app
)
from mysql.connector import Error as DBError

import db.core as db
from middleware import check_access
from utils import format_post



# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

bp = Blueprint('social', __name__, url_prefix='/social')


@bp.app_template_filter('format_post')
def format_post_filter(text):
    return format_post(text)


@bp.before_request
def restrict_access():
    """
    Enforce login requirements for all routes in this blueprint.
    """
    return check_access(['admin', 'user', 'social'])



# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------

@bp.route('/announcements')
def announcements():
    """
    Display the latest administrator announcements
    """
    
    posts = []
    conn = None

    try:
        conn = db.get_connection('social')
        posts = db.execute_procedure(conn, 'sp_fetch_announcements')
    except DBError as e:
        print(f"Social DB Error: {e}")
        # fail gracefully
    finally:
        if conn and conn.is_connected():
            conn.close()

    return render_template('announce.html', title='announcements', posts=posts)

# -----------------------------------------------------------------------------

@bp.route('/feed')
def feed():
    """
    User's personal activity feed.
    """
    return render_template('offline.html', title='feed')

# -----------------------------------------------------------------------------

@bp.route('/board')
def board():
    """
    Kanban board.
    """
    return render_template('offline.html', title='board')

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