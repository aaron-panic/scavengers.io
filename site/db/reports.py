# db.reports.py - Database routines for Reports Table (User + Admin)
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
# User Actions
# ---------------------------------------------------------

def create_report(u_id, target, description):
    conn = None
    try:
        conn = get_connection('user')
        execute_procedure(conn, 'sp_create_report', [u_id, target, description], commit=True)
    except Error:
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()

# ---------------------------------------------------------
# Admin Management
# ---------------------------------------------------------

def fetch_reports(limit=25, offset=0):
    conn = None
    reports = []
    try:
        conn = get_connection('admin_bot')
        reports = execute_procedure(conn, 'sp_admin_list_reports', [limit, offset])
    except Error:
        pass
    finally:
        if conn and conn.is_connected():
            conn.close()
    return reports

def update_report(report_id, status=None, message=None):
    conn = None
    try:
        conn = get_connection('admin_bot')
        execute_procedure(conn, 'sp_admin_update_report', [report_id, status, message], commit=True)
    except Error:
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()

def delete_report(report_id):
    conn = None
    try:
        conn = get_connection('admin_bot')
        execute_procedure(conn, 'sp_admin_delete_report', [report_id], commit=True)
    except Error:
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()