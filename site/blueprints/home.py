# home.py - Routing blueprint for / (site initial loading)
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

from flask import Blueprint, render_template, redirect, url_for, session
from middleware import check_access

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def start():
    # Redirects to the social feed if logged in, otherwise forces login
    if 'username' in session:
        return redirect(url_for('social.announce'))
    return redirect(url_for('auth.login'))
