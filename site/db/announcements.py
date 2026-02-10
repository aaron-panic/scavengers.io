# db.announcements.py - Database routines for Announcements Table (Users + Admin)
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
# Public / Social
# ---------------------------------------------------------

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
# Admin Management
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

def list_announcements_admin(limit, offset, sort_col='created_at', sort_dir='desc'):
    conn = None
    posts = []
    try:
        conn = get_connection('admin_bot')
        posts = execute_procedure(conn, 'sp_admin_list_announcements', [limit, offset, sort_col, sort_dir])
    except Error: pass
    finally:
        if conn and conn.is_connected(): conn.close()
    return posts