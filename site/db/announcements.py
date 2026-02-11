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

from typing import List, Dict, Any, Optional

from mysql.connector import Error
from .core import get_connection, execute_procedure

# -----------------------------------------------------------------------------
# Social
# -----------------------------------------------------------------------------

def fetch_announcements() -> List[Dict[str, Any]]:
    """
    Fetch the public feed of visible announcements.
    Calls: sp_fetch_announcements
    """

    conn = None
    posts = []
    try:
        conn = get_connection('social')
        posts = execute_procedure(conn, 'sp_fetch_announcements')
    except Error:
        pass
    finally:
        if conn and conn.is_connected():
            conn.close()
    return posts



# -----------------------------------------------------------------------------
# Admin
# -----------------------------------------------------------------------------

def admin_create_announcement(
    u_id: int, 
    title: str, 
    subtitle: Optional[str], 
    content: str, 
    footnote: Optional[str], 
    is_visible: bool
) -> None:
    """
    Create a new announcement.
    Calls: sp_admin_create_announcement
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_create_announcement', [u_id, title, subtitle, content, footnote, is_visible], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

# -----------------------------------------------------------------------------

def admin_update_announcement(
    id: int, 
    title: str, 
    subtitle: Optional[str], 
    content: str, 
    footnote: Optional[str], 
    is_visible: bool
) -> None:
    """
    Update an existing announcement.
    Calls: sp_admin_update_announcement
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_update_announcement', [id, title, subtitle, content, footnote, is_visible], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

# -----------------------------------------------------------------------------

def admin_delete_announcement(id: int) -> None:
    """
    Permanently delete an announcement.
    Calls: sp_admin_delete_announcement
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_delete_announcement', [id], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

# -----------------------------------------------------------------------------

def admin_fetch_announcement(id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch a single announcement by ID for editing.
    Calls: sp_admin_fetch_announcement
    """

    conn = None
    post = None
    try:
        conn = get_connection('admin')
        rows = execute_procedure(conn, 'sp_admin_fetch_announcement', [id])
        if rows:
            post = rows[0]
    except Error: pass
    finally:
        if conn and conn.is_connected(): conn.close()
    return post

# -----------------------------------------------------------------------------

def admin_fetch_announcements(
    limit: int, 
    offset: int, 
    sort_col: str = 'created_at', 
    sort_dir: str = 'desc'
) -> List[Dict[str, Any]]:
    """
    Fetch a paginated list of all announcements (including hidden).
    Calls: sp_admin_fetch_announcements
    """

    conn = None
    posts = []
    try:
        conn = get_connection('admin')
        posts = execute_procedure(conn, 'sp_admin_fetch_announcements', [limit, offset, sort_col, sort_dir])
    except Error: pass
    finally:
        if conn and conn.is_connected(): conn.close()
    return posts