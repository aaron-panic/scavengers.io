# middleware.py - RBAC functions
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

from flask import session, redirect, url_for, render_template

def check_access(allowed_roles):
    # Return to login if not logged in
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    # Render unauthorized if not allowed by role
    if session.get('role') not in allowed_roles:
        return render_template('unauthorized.html', title='unauthorized'), 403

    return None
