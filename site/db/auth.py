# db.auth.py - Database routines for /auth ('login')
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

from typing import List, Dict, Any, Optional

from mysql.connector import Error
from .core import get_connection, execute_procedure



# -----------------------------------------------------------------------------
# Public / Authentication
# -----------------------------------------------------------------------------

def fetch_user_auth(username: str) -> Optional[Dict[str, Any]]:
    """
    Fetch user data required for authentication (hash, role, status).
    Calls: sp_fetch_user_auth
    """
    conn = None
    user_data = None
    try:
        conn = get_connection('login')
        rows = execute_procedure(conn, 'sp_fetch_user_auth', [username])
        if rows:
            user_data = rows[0]
    except Error:
        pass
    finally:
        if conn and conn.is_connected():
            conn.close()
    return user_data

# -----------------------------------------------------------------------------

def create_user_request(username: str, password_hash: str, email: str) -> bool:
    """
    Submit a new user registration request.
    Returns True on success, False on duplicate/failure.
    Calls: sp_create_user_request
    """
    conn = None
    try:
        conn = get_connection('login')
        execute_procedure(
            conn, 
            'sp_create_user_request', 
            [username, password_hash, email], 
            commit=True
        )
        return True
    except Error as e:
        # Check for duplicate entry error (MySQL error 1062)
        if "Duplicate entry" in str(e):
            return False
        # Log other errors but don't crash
        print(f"Registration Error: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()