# db.requests.py - Database routines for Requests Table (User + Admin)
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
# User
# -----------------------------------------------------------------------------

def fetch_requests_by_status(
    status: str = 'all', 
    limit: int = 12, 
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Fetch requests filtered by status.
    Calls: sp_fetch_requests_by_status
    """

    conn = None
    requests = []
    try:
        conn = get_connection('user')
        requests = execute_procedure(conn, 'sp_fetch_requests_by_status', [status, limit, offset])
    except Error:
        pass
    finally:
        if conn and conn.is_connected():
            conn.close()
    return requests

# -----------------------------------------------------------------------------

def fetch_requests_by_user(
    u_id: int, 
    limit: int = 12, 
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Fetch requests submitted by a specific user.
    Calls: sp_fetch_requests_by_user
    """
    
    conn = None
    requests = []
    try:
        conn = get_connection('user')
        requests = execute_procedure(conn, 'sp_fetch_requests_by_user', [u_id, limit, offset])
    except Error:
        pass
    finally:
        if conn and conn.is_connected():
            conn.close()
    return requests

# -----------------------------------------------------------------------------

def create_request(
    u_id: int, 
    title: str, 
    description: str, 
    ref_1: Optional[str] = None, 
    ref_2: Optional[str] = None, 
    ref_3: Optional[str] = None
) -> None:
    """
    Submit a new media or feature request.
    Calls: sp_create_request
    """

    conn = None
    try:
        conn = get_connection('user')
        execute_procedure(conn, 'sp_create_request', [u_id, title, description, ref_1, ref_2, ref_3], commit=True)
    except Error:
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()



# -----------------------------------------------------------------------------
# Admin
# -----------------------------------------------------------------------------

def admin_fetch_requests(
    limit: int, 
    offset: int, 
    sort_col: str = 'created_at', 
    sort_dir: str = 'desc'
) -> List[Dict[str, Any]]:
    """
    Fetch a paginated list of all requests.
    Calls: sp_admin_fetch_requests
    """

    conn = None
    requests = []
    try:
        conn = get_connection('admin')
        requests = execute_procedure(conn, 'sp_admin_fetch_requests', [limit, offset, sort_col, sort_dir])
    except Error:
        pass
    finally:
        if conn and conn.is_connected():
            conn.close()
    return requests

# -----------------------------------------------------------------------------

def admin_fetch_request(id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch details of a single request.
    Calls: sp_admin_fetch_request
    """

    conn = None
    req = None
    try:
        conn = get_connection('admin')
        rows = execute_procedure(conn, 'sp_admin_fetch_request', [id])
        if rows:
            req = rows[0]
    except Error:
        pass
    finally:
        if conn and conn.is_connected():
            conn.close()
    return req

# -----------------------------------------------------------------------------

def admin_update_request(id: int, status: str, status_message: str) -> None:
    """
    Update request status and message.
    Calls: sp_admin_update_request
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_update_request', [id, status, status_message], commit=True)
    except Error:
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()

# -----------------------------------------------------------------------------

def admin_delete_request(id: int) -> None:
    """
    Permanently delete a request.
    Calls: sp_admin_delete_request
    """
    
    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_delete_request', [id], commit=True)
    except Error:
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()