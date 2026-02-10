# db.py - Database connections and retrieval/insertion functions
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

import os
import mysql.connector
from mysql.connector import Error
from flask import g

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
DB_HOST = "db"
DB_NAME = "scavengers"

ROLE_MAP = {
    'login_bot': 'DB_PASS_LOGIN_BOT',
    'admin_bot': 'DB_PASS_ADMIN_BOT',
    'admin': 'DB_PASS_ADMIN',
    'social': 'DB_PASS_SOCIAL',
    'user': 'DB_PASS_USER'
}

# ---------------------------------------------------------
# Execution Wrappers
# ---------------------------------------------------------

# Generic execution for Standard SQL (INSERT, UPDATE, DELETE, simple SELECT)
def execute_query(conn, query, params=None, commit=False):
    cursor = conn.cursor(dictionary=True)
    result = None
    try:
        cursor.execute(query, params or ())

        if commit:
            conn.commit()
            if query.strip().upper().startswith("INSERT"):
                result = cursor.lastrowid
            else:
                result = cursor.rowcount
        else:
            result = cursor.fetchall()

    except Error as e:
        print(f"Query execution error: {e}")
        raise
    finally:
        cursor.close()

    return result

# Generic execution for Stored Procedures (Handling callproc + stored_results)
# Returns: List of dictionaries (all rows from the first result set)
def execute_procedure(conn, proc_name, args=(), commit=False):
    cursor = conn.cursor(dictionary=True)
    results = []
    try:
        cursor.callproc(proc_name, args)
        
        if commit:
            conn.commit()
        
        for result in cursor.stored_results():
            rows = result.fetchall()
            if rows:
                results.extend(rows)

    except Error as e:
        print(f"Procedure execution error ({proc_name}): {e}")
        raise
    finally:
        cursor.close()

    return results

# ---------------------------------------------------------
# Connection Logic
# ---------------------------------------------------------

# Return proper connection based on role
def get_connection(role):
    if role not in ROLE_MAP:
        raise ValueError(f"Invalid Role: {role}")

    password = os.environ.get(ROLE_MAP[role])
    if not password:
        raise ValueError(f"Password for '{role}' not found in env vars.")

    try:
        conn = mysql.connector.connect(
            host = DB_HOST,
            database = DB_NAME,
            user = f"scav_{role}",
            password = password
        )
        return conn
    except Error as e:
        print(f"Error connecting to database as {role}: {e}")
        raise

# New Database connection based on role (Flask Context Aware)
def get_db(role='social'):
    if 'db_conns' not in g:
        g.db_conns = {}

    if role not in g.db_conns:
        g.db_conns[role] = get_connection(role)

    return g.db_conns[role]

# Close all open database connections
def close_dbs(e=None):
    db_conns = g.pop('db_conns', None)

    if db_conns:
        for role, conn in db_conns.items():
            if conn.is_connected():
                conn.close()

# ---------------------------------------------------------
# Data Access Objects
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
# Announcements
# ---------------------------------------------------------

# Fetch Announcements (Social)
def fetch_announcements():
    conn = None
    posts = []
    try:
        conn = get_connection('social')
        posts = execute_procedure(conn, 'sp_get_announcements')
    except Error:
        pass
    finally:
        if conn and conn.is_connected():
            conn.close()
    return posts

# ---------------------------------------------------------
# User Management (Admin)
# ---------------------------------------------------------

# Fetch users for admin panel (Admin)
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

# Approve newly requested user (Admin)
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

# Deny newly requested user (Admin)
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

# Fetch all user details except password_hash (Admin)
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

# Suspend (Admin)
def suspend_user(user_id, hours):
    conn = None
    try:
        conn = get_connection('admin_bot')
        execute_procedure(conn, 'sp_admin_suspend_user', [user_id, hours], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

# Ban (Admin)
def ban_user(user_id):
    conn = None
    try:
        conn = get_connection('admin_bot')
        execute_procedure(conn, 'sp_admin_ban_user', [user_id], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

# Reinstate (Admin)
def reinstate_user(user_id):
    conn = None
    try:
        conn = get_connection('admin_bot')
        execute_procedure(conn, 'sp_admin_reinstate_user', [user_id], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

# Delete (Admin)
def delete_user(user_id):
    conn = None
    try:
        conn = get_connection('admin_bot')
        execute_procedure(conn, 'sp_admin_delete_user', [user_id], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

# Reset Password (Admin)
def reset_password(user_id, new_hash):
    conn = None
    try:
        conn = get_connection('admin_bot')
        execute_procedure(conn, 'sp_admin_reset_password', [user_id, new_hash], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

# ---------------------------------------------------------
# Announcement Management (Admin)
# ---------------------------------------------------------

def create_announcement(uid, title, subtitle, content, footnote, is_visible):
    conn = None
    try:
        conn = get_connection('admin_bot')
        execute_procedure(conn, 'sp_admin_create_announcement', [uid, title, subtitle, content, footnote, is_visible], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

def update_announcement(id, title, subtitle, content, footnote, is_visible):
    conn = None
    try:
        conn = get_connection('admin_bot')
        execute_procedure(conn, 'sp_admin_update_announcement', [id, title, subtitle, content, footnote, is_visible], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

def delete_announcement(id):
    conn = None
    try:
        conn = get_connection('admin_bot')
        execute_procedure(conn, 'sp_admin_delete_announcement', [id], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

def get_announcement(id):
    conn = None
    post = None
    try:
        conn = get_connection('admin_bot')
        rows = execute_procedure(conn, 'sp_admin_get_announcement', [id])
        if rows:
            post = rows[0]
    except Error: pass
    finally:
        if conn and conn.is_connected(): conn.close()
    return post

def list_announcements_admin(limit, offset):
    conn = None
    posts = []
    try:
        conn = get_connection('admin_bot')
        posts = execute_procedure(conn, 'sp_admin_list_announcements', [limit, offset])
    except Error: pass
    finally:
        if conn and conn.is_connected(): conn.close()
    return posts