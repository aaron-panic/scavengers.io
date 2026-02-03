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

from flask import Blueprint, render_template
from middleware import check_access

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.before_request
def restrict_access():
    return check_access(['admin','user'])

@user_bp.route('/media')
def media():
    return render_template('media.html', title='media')

@user_bp.route('/req')
def req():
    return render_template('req.html', title='req')

@user_bp.route('/report')
def report():
    return render_template('report.html', title='report')

@user_bp.route('/dev')
def dev():
    return render_template('dev.html', title='dev')
