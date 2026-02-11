# db.users.py - Database routines for Users Table (Login + Admin)
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
# Login
# -----------------------------------------------------------------------------

def fetch_user_auth(username: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve password hash, role, and status for login authentication.
    Calls: sp_fetch_user_auth
    """

    conn = None
    auth_data = None
    try:
        conn = get_connection('login')
        rows = execute_procedure(conn, 'sp_fetch_user_auth', [username])
        if rows:
            auth_data = rows[0]
    except Error:
        pass
    finally:
        if conn and conn.is_connected():
            conn.close()
    return auth_data



# -----------------------------------------------------------------------------
# Admin
# -----------------------------------------------------------------------------

def admin_fetch_users(
    limit: int, 
    offset: int, 
    sort_col: str, 
    sort_dir: str
) -> List[Dict[str, Any]]:
    """
    Retrieve a paginated list of users.
    Calls: sp_admin_fetch_users
    """

    conn = None
    users = []
    try:
        conn = get_connection('admin')
        users = execute_procedure(conn, 'sp_admin_fetch_users', [limit, offset, sort_col, sort_dir])
    except Error:
        pass
    finally:
        if conn and conn.is_connected():
            conn.close()
    return users

# -----------------------------------------------------------------------------

def admin_approve_user(id: int) -> None:
    """
    Promote a requested user to active status.
    Calls: sp_admin_approve_user
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_approve_user', [id], commit=True)
    except Error:
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()

# -----------------------------------------------------------------------------

def admin_deny_user(id: int) -> None:
    """
    Delete (deny) a user request.
    Calls: sp_admin_deny_user
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_deny_user', [id], commit=True)
    except Error:
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()

# -----------------------------------------------------------------------------

def admin_fetch_user(id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve full profile details for a specific user.
    Calls: sp_admin_fetch_user
    """

    conn = None
    user_data = None
    try:
        conn = get_connection('admin')
        rows = execute_procedure(conn, 'sp_admin_fetch_user', [id])
        if rows:
            user_data = rows[0]
    except Error:
        pass
    finally:
        if conn and conn.is_connected():
            conn.close()
    return user_data

# -----------------------------------------------------------------------------

def admin_suspend_user(id: int, hours: int) -> None:
    """
    Set user status to suspended for a specified duration.
    Calls: sp_admin_suspend_user
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_suspend_user', [id, hours], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

# -----------------------------------------------------------------------------

def admin_ban_user(id: int) -> None:
    """
    Permanently ban a user.
    Calls: sp_admin_ban_user
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_ban_user', [id], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

# -----------------------------------------------------------------------------

def admin_reinstate_user(id: int) -> None:
    """
    Restore a user to active status.
    Calls: sp_admin_reinstate_user
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_reinstate_user', [id], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

# -----------------------------------------------------------------------------

def admin_delete_user(id: int) -> None:
    """
    Permanently delete a user record.
    Calls: sp_admin_delete_user
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_delete_user', [id], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

# -----------------------------------------------------------------------------

def admin_reset_password(id: int, password_hash: str) -> None:
    """
    Force update a user's password hash.
    Calls: sp_admin_reset_password
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_reset_password', [id, password_hash], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()