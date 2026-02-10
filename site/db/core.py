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