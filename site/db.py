import os
import mysql.connector
from mysql.connector import Error
from flask import g

# Configuration from Environment
DB_HOST = "db"
DB_NAME = "scavengers"

ROLE_MAP = {
    'login_bot': 'DB_PASS_LOGIN_BOT',
    'admin_bot': 'DB_PASS_ADMIN_BOT',
    'admin': 'DB_PASS_ADMIN',
    'social': 'DB_PASS_SOCIAL',
    'user': 'DB_PASS_USER'
}

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

# Generic execution function
# conn: Active Database connection object
# query: SQL String
# params: Paramaters to expand in string (tuple)
# commit: Set to True for INSERT/UPDATE/DELTE
# Returns list of dictionaries with SELECT
# Returns LastRowID with INSERT
# Returns RowCount with UPDATE/DELETE
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

# Connects as 'scav_login_bot' and retrieves password hash for username with (STORED PROCEDURE)
def fetch_user_auth(username):
    conn = None
    auth_data = None

    try:
        conn = get_connection('login_bot')
        cursor = conn.cursor(dictionary=True)

        cursor.callproc('sp_get_user_auth', [username])

        for result in cursor.stored_results():
            rows = result.fetchall()
            if rows:
                auth_data = rows[0]
    
    except Error as e:
        print(f"Authentication fetch error: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

    return auth_data

# New Database connection based on role
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

# Fetch users for admin panel (STORED PROCEDURE)
def fetch_all_users():
    conn = None
    users = []

    try:
        conn = get_connection('admin_bot')
        cursor = conn.cursor(dictionary=True)

        cursor.callproc('sp_admin_list_users')

        for result in cursor.stored_results():
            users = result.fetchall()

    except Error as e:
        print(f"Admin fetch error: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

    return users

# Approve newly requested user
def approve_user(user_id):
    conn = None
    try:
        conn = get_connection('admin_bot')
        execute_query(conn, "CALL sp_admin_approve_requested(%s)", (user_id,), commit=True)
    except Error as e:
        print(f"Approve error: {e}")
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()

# Deny newly requested user
def deny_user(user_id):
    conn = None
    try:
        conn = get_connection('admin_bot')
        execute_query(conn, "CALL sp_admin_deny_requested(%s)", (user_id,), commit=True)
    except Error as e:
        print(f"Deny error: {e}")
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()