-- 02_users_admin.sql - Stored procedures for Users table ('admin')
-- Copyright (C) 2026 Aaron Reichenbach
--
-- This program is free software: you can redistribute it and/or modify         
-- it under the terms of the GNU Affero General Public License as
-- published by the Free Software Foundation, either version 3 of the
-- License, or (at your option) any later version.

-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU Affero General Public License for more details.

-- You should have received a copy of the GNU Affero General Public License
-- along with this program.  If not, see <https://www.gnu.org/licenses/>.



DELIMITER //

-- sp_admin_fetch_users(p_limit, p_offset, p_sort_col, p_sort_dir)
-- ----------------------------------------------------------------------------
-- Desc:
--      Retrieve a paginated list of users.
-- Params:
--      p_limit (INT)                   Number of records to retrieve for a page view
--      p_offset (INT)                  Where to start retrieving records for page view
--      p_sort_col (VARCHAR 20)         Column to sort by
--      p_sort_dir (VARCHAR 4)          Direction (ASC or DESC) to sort
-- Notes:
--      This function updates status for all users to remove suspended status
--      if past the suspension_until timestamp.

CREATE PROCEDURE sp_admin_fetch_users(
    IN p_limit INT,
    IN p_offset INT,
    IN p_sort_col VARCHAR(20),
    IN p_sort_dir VARCHAR(4)
)
BEGIN

    -- Hard caps to ensure that there's no nonsense from the caller
    IF p_limit > 100 THEN
        SET p_limit = 100;
    END IF;
    IF p_limit <= 0 THEN
        SET p_limit = 25;
    END IF;

    -- This is the status update from Notes above
    UPDATE Users
    SET status = 'active', suspended_until = NULL
    WHERE status = 'suspended'
        AND suspended_until <= NOW();

    -- Fetch data with total count so caller can calculate number of pages
    SELECT
        id,
        username,
        email,
        role,
        status,
        suspended_until,
        created_at,
        updated_at,
        COUNT(*) OVER() as total_records
    FROM Users
    ORDER BY

        -- Integer Sorting (id)
        CASE WHEN p_sort_col = 'id' AND UPPER(p_sort_dir) = 'ASC' THEN id END ASC,
        CASE WHEN p_sort_col = 'id' AND UPPER(p_sort_dir) = 'DESC' THEN id END DESC,
        
        -- String Sorting (username, role, status)
        CASE WHEN p_sort_col = 'username' AND UPPER(p_sort_dir) = 'ASC' THEN username END ASC,
        CASE WHEN p_sort_col = 'username' AND UPPER(p_sort_dir) = 'DESC' THEN username END DESC,
        
        CASE WHEN p_sort_col = 'role' AND UPPER(p_sort_dir) = 'ASC' THEN role END ASC,
        CASE WHEN p_sort_col = 'role' AND UPPER(p_sort_dir) = 'DESC' THEN role END DESC,
        
        CASE WHEN p_sort_col = 'status' AND UPPER(p_sort_dir) = 'ASC' THEN status END ASC,
        CASE WHEN p_sort_col = 'status' AND UPPER(p_sort_dir) = 'DESC' THEN status END DESC

    LIMIT p_limit OFFSET p_offset;

END //



-- sp_admin_approve_user(p_id)
-- ----------------------------------------------------------------------------
-- Desc:
--      Promote a requested user to active status.
-- Params:
--      p_id (INT)                      User id (matches Users.id)

CREATE PROCEDURE sp_admin_approve_user(
    IN p_id INT
)
BEGIN

    UPDATE Users
    SET status = 'active'
        WHERE id = p_id
        AND status = 'requested';

END //



-- sp_admin_deny_user(p_id)
-- ----------------------------------------------------------------------------
-- Desc:
--      Delete (deny) a user request.
-- Params:
--      p_id (INT)                      User id (matches Users.id)

CREATE PROCEDURE sp_admin_deny_user(
    IN p_id INT
)
BEGIN

    DELETE FROM Users
        WHERE id = p_id
        AND status = 'requested';

END //



-- sp_admin_fetch_user_details(p_id)
-- ----------------------------------------------------------------------------
-- Desc:
--      Retrieve full profile details for a specific user.
-- Params:
--      p_id (INT)                      User id (matches Users.id)

CREATE PROCEDURE sp_admin_fetch_user_details(
    IN p_id INT
)
BEGIN

    SELECT
        id,
        username,
        email,
        role,
        status,
        suspended_until,
        created_at,
        updated_at
    FROM Users
    WHERE id = p_id;

END //



-- sp_admin_suspend_user(p_id, p_hours)
-- ----------------------------------------------------------------------------
-- Desc:
--      Set user status to suspended for a specified duration.
-- Params:
--      p_id (INT)                      User id (matches Users.id)
--      p_hours (INT)                   Duration of suspension (hours)

CREATE PROCEDURE sp_admin_suspend_user(IN p_id INT, IN p_hours INT)
BEGIN

    UPDATE Users 
    SET status = 'suspended', 
        suspended_until = DATE_ADD(NOW(), INTERVAL p_hours HOUR)
    WHERE id = p_id;

END //



-- sp_admin_ban_user(p_id)
-- ----------------------------------------------------------------------------
-- Desc:
--      Permanently ban a user.
-- Params:
--      p_id (INT)                      User id (matches Users.id)

CREATE PROCEDURE sp_admin_ban_user(IN p_id INT)
BEGIN

    -- No need for a suspension time if banned - reinstate immediately makes
    -- the user 'active' again and clears the timer anyway
    UPDATE Users 
    SET status = 'banned', 
        suspended_until = NULL 
    WHERE id = p_id;

END //



-- sp_admin_reinstate_user(p_id)
-- ----------------------------------------------------------------------------
-- Desc:
--      Restore a user to active status.
-- Params:
--      p_id (INT)                      User id (matches Users.id)

CREATE PROCEDURE sp_admin_reinstate_user(IN p_id INT)
BEGIN

    UPDATE Users 
    SET status = 'active', 
        suspended_until = NULL 
    WHERE id = p_id;

END //



-- sp_admin_delete_user(p_id)
-- ----------------------------------------------------------------------------
-- Desc:
--      Permanently delete a user record.
-- Params:
--      p_id (INT)                      User id (matches Users.id)

CREATE PROCEDURE sp_admin_delete_user(IN p_id INT)
BEGIN

    DELETE FROM Users WHERE id = p_id;

END //



-- sp_admin_reset_password(p_id, p_hash)
-- ----------------------------------------------------------------------------
-- Desc:
--      Force update a user's password hash.
-- Params:
--      p_id (INT)                      User id (matches Users.id)
--      p_hash (VARCHAR 255)            New password hash provided to procedure

CREATE PROCEDURE sp_admin_reset_password(IN p_id INT, IN p_hash VARCHAR(255))
BEGIN

    UPDATE Users
    SET password_hash = p_hash
    WHERE id = p_id;

END //

DELIMITER ;