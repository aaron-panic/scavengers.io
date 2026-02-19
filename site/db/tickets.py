# db.tickets.py - Database routines for Tickets Tables (Users + Admin)
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

def create_ticket(
    u_id: int,
    ticket_type: str,
    title: str,
    description: str,
    priority: Optional[str] = None
) -> None:
    """
    Submit a new ticket.
    Calls: sp_create_ticket
    """

    conn = None
    try:
        conn = get_connection('user')
        execute_procedure(conn, 'sp_create_ticket', [u_id, ticket_type, title, description, priority], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

# -----------------------------------------------------------------------------

def fetch_tickets(
    ticket_type: Optional[str],
    status: Optional[str],
    tag_name: Optional[str],
    limit: int,
    offset: int
) -> List[Dict[str, Any]]:
    """
    Fetch tickets with optional filtering by type, status, and tag.
    Calls: sp_fetch_tickets
    """

    conn = None
    tickets = []
    try:
        conn = get_connection('user')
        tickets = execute_procedure(conn, 'sp_fetch_tickets', [ticket_type, status, tag_name, limit, offset])
    except Error: pass
    finally:
        if conn and conn.is_connected(): conn.close()
    return tickets

# -----------------------------------------------------------------------------

def fetch_tickets_by_user(
    u_id: int,
    ticket_type: Optional[str],
    status: Optional[str],
    tag_name: Optional[str],
    limit: int,
    offset: int
) -> List[Dict[str, Any]]:
    """
    Fetch tickets submitted by a single user with optional filtering.
    Calls: sp_fetch_tickets_by_user
    """

    conn = None
    tickets = []
    try:
        conn = get_connection('user')
        tickets = execute_procedure(conn, 'sp_fetch_tickets_by_user', [u_id, ticket_type, status, tag_name, limit, offset])
    except Error: pass
    finally:
        if conn and conn.is_connected(): conn.close()
    return tickets

# -----------------------------------------------------------------------------

def fetch_ticket(id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch a single ticket by ID.
    Calls: sp_fetch_ticket
    """

    conn = None
    ticket = None
    try:
        conn = get_connection('user')
        rows = execute_procedure(conn, 'sp_fetch_ticket', [id])
        if rows:
            ticket = rows[0]
    except Error: pass
    finally:
        if conn and conn.is_connected(): conn.close()
    return ticket

# -----------------------------------------------------------------------------

def fetch_ticket_status_messages(ticket_id: int) -> List[Dict[str, Any]]:
    """
    Fetch status history for a ticket.
    Calls: sp_fetch_ticket_status_messages
    """

    conn = None
    messages = []
    try:
        conn = get_connection('user')
        messages = execute_procedure(conn, 'sp_fetch_ticket_status_messages', [ticket_id])
    except Error: pass
    finally:
        if conn and conn.is_connected(): conn.close()
    return messages

# -----------------------------------------------------------------------------



def fetch_ticket_tag_list() -> List[Dict[str, Any]]:
    """
    Fetch all active tags ordered by name.
    Calls: sp_fetch_ticket_tag_list
    """

    conn = None
    tags = []
    try:
        conn = get_connection('user')
        tags = execute_procedure(conn, 'sp_fetch_ticket_tag_list')
    except Error:
        pass
    finally:
        if conn and conn.is_connected():
            conn.close()
    return tags

# -----------------------------------------------------------------------------
def fetch_ticket_tags(ticket_id: int) -> List[Dict[str, Any]]:
    """
    Fetch tags linked to a ticket.
    Calls: sp_fetch_ticket_tags
    """

    conn = None
    tags = []
    try:
        conn = get_connection('user')
        tags = execute_procedure(conn, 'sp_fetch_ticket_tags', [ticket_id])
    except Error: pass
    finally:
        if conn and conn.is_connected(): conn.close()
    return tags


# -----------------------------------------------------------------------------
# Admin
# -----------------------------------------------------------------------------

def admin_fetch_tickets(
    ticket_type: Optional[str],
    status: Optional[str],
    assigned_admin_u_id: Optional[int],
    tag_name: Optional[str],
    limit: int,
    offset: int
) -> List[Dict[str, Any]]:
    """
    Fetch tickets for admin workflows with optional filters.
    Calls: sp_admin_fetch_tickets
    """

    conn = None
    tickets = []
    try:
        conn = get_connection('admin')
        tickets = execute_procedure(conn, 'sp_admin_fetch_tickets', [ticket_type, status, assigned_admin_u_id, tag_name, limit, offset])
    except Error: pass
    finally:
        if conn and conn.is_connected(): conn.close()
    return tickets

# -----------------------------------------------------------------------------

def admin_fetch_ticket(id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch one ticket by ID for admin views.
    Calls: sp_admin_fetch_ticket
    """

    conn = None
    ticket = None
    try:
        conn = get_connection('admin')
        rows = execute_procedure(conn, 'sp_admin_fetch_ticket', [id])
        if rows:
            ticket = rows[0]
    except Error: pass
    finally:
        if conn and conn.is_connected(): conn.close()
    return ticket

# -----------------------------------------------------------------------------

def admin_update_ticket(
    id: int,
    status: Optional[str],
    priority: Optional[str]
) -> None:
    """
    Update a ticket status and/or priority.
    Calls: sp_admin_update_ticket
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_update_ticket', [id, status, priority], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

# -----------------------------------------------------------------------------

def admin_create_ticket_status_message(
    ticket_id: int,
    changed_by_u_id: int,
    old_status: str,
    new_status: str,
    status_message: str
) -> None:
    """
    Add a status history message to a ticket.
    Calls: sp_admin_create_ticket_status_message
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_create_ticket_status_message', [ticket_id, changed_by_u_id, old_status, new_status, status_message], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

# -----------------------------------------------------------------------------

def admin_update_ticket_status_message(
    id: int,
    old_status: Optional[str],
    new_status: Optional[str],
    status_message: Optional[str]
) -> None:
    """
    Update a status history message.
    Calls: sp_admin_update_ticket_status_message
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_update_ticket_status_message', [id, old_status, new_status, status_message], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

# -----------------------------------------------------------------------------

def admin_delete_ticket_status_message(id: int) -> None:
    """
    Soft delete a status history message.
    Calls: sp_admin_delete_ticket_status_message
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_delete_ticket_status_message', [id], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

# -----------------------------------------------------------------------------

def admin_create_ticket_tag(name: str) -> None:
    """
    Create (or restore) a ticket tag.
    Calls: sp_admin_create_ticket_tag
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_create_ticket_tag', [name], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

# -----------------------------------------------------------------------------

def admin_link_ticket_tag(ticket_id: int, tag_id: int) -> None:
    """
    Link a tag to a ticket.
    Calls: sp_admin_link_ticket_tag
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_link_ticket_tag', [ticket_id, tag_id], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

# -----------------------------------------------------------------------------

def admin_unlink_ticket_tag(ticket_id: int, tag_id: int) -> None:
    """
    Unlink (soft-delete) a tag from a ticket.
    Calls: sp_admin_unlink_ticket_tag
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_unlink_ticket_tag', [ticket_id, tag_id], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

# -----------------------------------------------------------------------------

def admin_assign_ticket(ticket_id: int, assigned_admin_u_id: int, assigned_by_u_id: int) -> None:
    """
    Assign an admin user to a ticket.
    Calls: sp_admin_assign_ticket
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_assign_ticket', [ticket_id, assigned_admin_u_id, assigned_by_u_id], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

# -----------------------------------------------------------------------------

def admin_unassign_ticket(ticket_id: int, assigned_admin_u_id: int) -> None:
    """
    Remove an admin assignment from a ticket.
    Calls: sp_admin_unassign_ticket
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_unassign_ticket', [ticket_id, assigned_admin_u_id], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()

# -----------------------------------------------------------------------------

def admin_fetch_ticket_assignments(ticket_id: int) -> List[Dict[str, Any]]:
    """
    Fetch active admin assignments for a ticket.
    Calls: sp_admin_fetch_ticket_assignments
    """

    conn = None
    assignments = []
    try:
        conn = get_connection('admin')
        assignments = execute_procedure(conn, 'sp_admin_fetch_ticket_assignments', [ticket_id])
    except Error: pass
    finally:
        if conn and conn.is_connected(): conn.close()
    return assignments

# -----------------------------------------------------------------------------

def admin_delete_ticket(id: int) -> None:
    """
    Soft delete a ticket.
    Calls: sp_admin_delete_ticket
    """

    conn = None
    try:
        conn = get_connection('admin')
        execute_procedure(conn, 'sp_admin_delete_ticket', [id], commit=True)
    except Error: raise
    finally:
        if conn and conn.is_connected(): conn.close()
