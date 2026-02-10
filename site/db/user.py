# db.users.py - Database routines for Users Table (User Authentication + Admin)
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

from mysql.connector import Error
from .core import get_connection, execute_procedure

# ---------------------------------------------------------
# Authentication
# ---------------------------------------------------------

# Fetch password_hash for username (Login)
def fetch_user_auth(username):
    conn = None
    auth_data = None
    try:
        conn = get_connection('login_bot')
        rows = execute_procedure(conn, 'sp_get_user_auth', [username])
        if rows:
            auth_data = rows[0]
    except Error:
        pass
    finally:
        if conn and conn.is_connected():
            conn.close()
    return auth_data

# ---------------------------------------------------------
# Admin User Management
# ---------------------------------------------------------

def fetch_all_users(limit, offset, sort_col, sort_dir):
    conn = None
    users = []
    try:
        conn = get_connection('admin_bot')
        users = execute_procedure(conn, 'sp_admin_list_users', [limit, offset, sort_col, sort_dir])
    except Error:
        pass
    finally:
        if conn and conn.is_connected():
            conn.close()
    return users

# Approve user creation request
def approve_user(user_id):
    conn = None
    try:
        conn = get_connection('admin_bot')
        # Note: We use execute_procedure with commit=True for actions
        execute_procedure(conn, 'sp_admin_approve_requested', [user_id], commit=True)
    except Error:
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()

# Deny user creation request
def deny_user(user_id):
    conn = None
    try:
        conn = get_connection('admin_bot')
        execute_procedure(conn, 'sp_admin_deny_requested', [user_id], commit=True)
    except Error:
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()

# Fetch all user details except password_hash
def fetch_user_details(user_id):
    conn = None
    user_data = None
    try:
        conn = get_connection('admin_bot')
        rows = execute_procedure(conn, 'sp_admin_get_user_details', [user_id])
        if rows:
            user_data = rows[0]
    except Error:
        pass
    finally:
        if conn and conn.is_connected():
            conn.close()
    return user_data

def suspend_user(user_id, hours):
    conn = None
    try:
        conn = get_connection('admin_bot')
        execute_procedure(conn, 'sp_admin_suspend_user', [user_id, hours], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

def ban_user(user_id):
    conn = None
    try:
        conn = get_connection('admin_bot')
        execute_procedure(conn, 'sp_admin_ban_user', [user_id], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

def reinstate_user(user_id):
    conn = None
    try:
        conn = get_connection('admin_bot')
        execute_procedure(conn, 'sp_admin_reinstate_user', [user_id], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

def delete_user(user_id):
    conn = None
    try:
        conn = get_connection('admin_bot')
        execute_procedure(conn, 'sp_admin_delete_user', [user_id], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

def reset_password(user_id, new_hash):
    conn = None
    try:
        conn = get_connection('admin_bot')
        execute_procedure(conn, 'sp_admin_reset_password', [user_id, new_hash], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()