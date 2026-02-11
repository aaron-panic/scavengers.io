# db.core.py - Database connections and execution wrappers
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
from typing import List, Dict, Any, Optional, Union

import mysql.connector
from mysql.connector import Error
from flask import g

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
DB_HOST = "db"
DB_NAME = "scavengers"

ROLE_MAP = {
    'login': 'DB_PASS_LOGIN',
    'admin': 'DB_PASS_ADMIN',
    'social': 'DB_PASS_SOCIAL',
    'user': 'DB_PASS_USER'
}

# -----------------------------------------------------------------------------
# Connection Logic
# -----------------------------------------------------------------------------

def get_connection(role: str) -> mysql.connector.connection.MySQLConnection:
    """
    Establish and return a database connection based on the requested role.

    :param role: The role key ('login', 'admin', 'user' or 'social') mapping to credentials.
    :return: A generic MySQLConnection object.
    :raises ValueError: If the role is invalid or credentials are missing.
    """
    
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

# -----------------------------------------------------------------------------

def get_db(role: str = 'UNDEFINED_ROLE') -> mysql.connector.connection.MySQLConnection:
    """
    Retrieve a database connection for the current Flask application context.
    Creates a new connection if one does not exist for the specified role.

    :param role: The role key to connect as.
    :return: The active MySQLConnection for this context.
    """

    if 'db_conns' not in g:
        g.db_conns = {}

    if role not in g.db_conns:
        g.db_conns[role] = get_connection(role)

    return g.db_conns[role]

# -----------------------------------------------------------------------------

def close_dbs(e: Optional[BaseException] = None) -> None:
    """
    Close all database connections stored in the Flask global context (g).

    :param e: Optional exception that caused the teardown (unused).
    """

    db_conns = g.pop('db_conns', None)

    if db_conns:
        for role, conn in db_conns.items():
            if conn.is_connected():
                conn.close()    



# -----------------------------------------------------------------------------
# Execution Wrapper
# -----------------------------------------------------------------------------

def execute_procedure(
    conn: mysql.connector.connection.MySQLConnection, 
    proc_name: str, 
    args: tuple = (), 
    commit: bool = False
) -> List[Dict[str, Any]]:
    """
    Execute a stored procedure and return the result set.

    :param conn: The active database connection.
    :param proc_name: The name of the stored procedure to call.
    :param args: A tuple of arguments to pass to the procedure.
    :param commit: If True, commits the transaction after execution.
    :return: A list of dictionaries representing the rows returned by the procedure.
    """
    
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