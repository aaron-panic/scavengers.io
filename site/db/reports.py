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

from typing import List, Dict, Any, Optional

from mysql.connector import Error
from .core import get_connection, execute_procedure

# -----------------------------------------------------------------------------
# User
# -----------------------------------------------------------------------------

def create_report(u_id: int, target: str, description: str) -> None:
    """
    Submit a new issue or report.
    Calls: sp_create_report
    """
    conn = None
    try:
        conn = get_connection('user')
        execute_procedure(conn, 'sp_create_report', [u_id, target, description], commit=True)
    except Error:
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()



# -----------------------------------------------------------------------------
# Admin
# -----------------------------------------------------------------------------

def admin_fetch_reports(
    limit: int = 25, 
    offset: int = 0, 
    sort_col: str = 'created_at', 
    sort_dir: str = 'desc'
) -> List[Dict[str, Any]]:
    """
    Fetch a paginated list of reports.
    Calls: sp_admin_fetch_reports
    """

    conn = None
    reports = []
    try:
        conn = get_connection('admin')
        reports = execute_procedure(conn, 'sp_admin_fetch_reports', [limit, offset, sort_col, sort_dir])
    except Error:
        pass
    finally:
        if conn and conn.is_connected():
            conn.close()
    return reports

# -----------------------------------------------------------------------------

def admin_fetch_report(id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch details of a single report.
    Calls: sp_admin_fetch_report
    """

    conn = None
    report = None
    try:
        conn = get_connection('admin')
        rows = execute_procedure(conn, 'sp_admin_fetch_report', [id])
        if rows:
            report = rows[0]
    except Error:
        pass
    finally:
        if conn and conn.is_connected():
            conn.close()
    return report

# -----------------------------------------------------------------------------

def admin_update_report(
    id: int,
    status: Optional[str] = None,
    status_message: Optional[str] = None
) -> None:
    """
    Update the status or message of a report.
    Calls: sp_admin_update_report
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_update_report', [id, status, status_message], commit=True)
    except Error:
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()

# -----------------------------------------------------------------------------

def admin_delete_report(id: int) -> None:
    """
    Permanently delete a report.
    Calls: sp_admin_delete_report
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_delete_report', [id], commit=True)
    except Error:
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()