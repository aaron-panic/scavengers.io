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

from mysql.connector import Error
from .core import get_connection, execute_procedure

# ---------------------------------------------------------
# Request Retrieval
# ---------------------------------------------------------

def fetch_requests_by_status(status='all', limit=12, offset=0):
    conn = None
    requests = []
    try:
        conn = get_connection('user')
        requests = execute_procedure(conn, 'sp_get_requests_by_status', [status, limit, offset])
    except Error:
        pass
    finally:
        if conn and conn.is_connected():
            conn.close()
    return requests

def fetch_requests_by_uid(uid=None, limit=12, offset=0):
    conn = None
    requests = []
    try:
        conn = get_connection('user')
        requests = execute_procedure(conn, 'sp_get_requests_by_uid', [uid, limit, offset])
    except Error:
        pass
    finally:
        if conn and conn.is_connected():
            conn.close()
    return requests

# ---------------------------------------------------------
# User Actions
# ---------------------------------------------------------

def create_request(u_id, title, description, ref_1=None, ref_2=None, ref_3=None):
    conn = None
    try:
        conn = get_connection('user')
        execute_procedure(conn, 'sp_create_request', [u_id, title, description, ref_1, ref_2, ref_3], commit=True)
    except Error:
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()

# ---------------------------------------------------------
# Admin Management
# ---------------------------------------------------------

def list_requests_admin(limit, offset, sort_col='created_at', sort_dir='desc'):
    conn = None
    requests = []
    try:
        conn = get_connection('admin_bot')
        requests = execute_procedure(conn, 'sp_admin_list_requests', [limit, offset, sort_col, sort_dir])
    except Error:
        pass
    finally:
        if conn and conn.is_connected():
            conn.close()
    return requests

def get_request(request_id):
    conn = None
    req = None
    try:
        conn = get_connection('admin_bot')
        rows = execute_procedure(conn, 'sp_admin_get_request', [request_id])
        if rows:
            req = rows[0]
    except Error:
        pass
    finally:
        if conn and conn.is_connected():
            conn.close()
    return req

def update_request(request_id, status, message):
    conn = None
    try:
        conn = get_connection('admin_bot')
        execute_procedure(conn, 'sp_admin_update_request', [request_id, status, message], commit=True)
    except Error:
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()

def delete_request(request_id):
    conn = None
    try:
        conn = get_connection('admin_bot')
        execute_procedure(conn, 'sp_admin_delete_request', [request_id], commit=True)
    except Error:
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()