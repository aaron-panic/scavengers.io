# admin.py - Routing blueprint for /social (social networking features)
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

from flask import Blueprint, render_template
from middleware import check_access
import db
from utils import format_post

social_bp = Blueprint('social', __name__, url_prefix='/social')

@social_bp.app_template_filter('format_post')
def format_post_filter(text):
    return format_post(text)

@social_bp.before_request
def restrict_access():
    return check_access(['admin', 'user', 'social'])

@social_bp.route('/announce')
def announce():
    posts = db.fetch_announcements()
    return render_template('announce.html', title='social.announce', posts=posts)

@social_bp.route('/feed')
def feed():
    return render_template('offline.html', title='social.feed')

@social_bp.route('/board')
def board():
    return render_template('offline.html', title='social.board')

@social_bp.route('/chat')
def chat():
    return render_template('offline.html', title='social.chat')

@social_bp.route('/profile')
def profile():
    return render_template('offline.html', title='social.profile')