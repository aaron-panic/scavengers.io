-- 02_admin_procs.sql - Stored procedures for admin tasks
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

-- List All Users
DELIMITER //

-- List All Users
CREATE PROCEDURE sp_admin_list_users(
    IN p_limit INT,
    IN p_offset INT,
    IN p_sort_col VARCHAR(20),
    IN p_sort_dir VARCHAR(4)
)
BEGIN
    -- Maintenance: Remove expired suspensions
    UPDATE Users
    SET status = 'active', suspended_until = NULL
    WHERE status = 'suspended'
        AND suspended_until <= NOW();

    -- Fetch Data with Total Count
    SELECT
        id,
        username,
        email,
        role,
        status,
        suspended_until,
        created_at,
        COUNT(*) OVER() as total_records
    FROM Users
    ORDER BY
        -- Integer Sorting (ID)
        CASE WHEN p_sort_col = 'id' AND UPPER(p_sort_dir) = 'ASC' THEN id END ASC,
        CASE WHEN p_sort_col = 'id' AND UPPER(p_sort_dir) = 'DESC' THEN id END DESC,
        
        -- String Sorting (Username, Role, Status)
        CASE WHEN p_sort_col = 'username' AND UPPER(p_sort_dir) = 'ASC' THEN username END ASC,
        CASE WHEN p_sort_col = 'username' AND UPPER(p_sort_dir) = 'DESC' THEN username END DESC,
        
        CASE WHEN p_sort_col = 'role' AND UPPER(p_sort_dir) = 'ASC' THEN role END ASC,
        CASE WHEN p_sort_col = 'role' AND UPPER(p_sort_dir) = 'DESC' THEN role END DESC,
        
        CASE WHEN p_sort_col = 'status' AND UPPER(p_sort_dir) = 'ASC' THEN status END ASC,
        CASE WHEN p_sort_col = 'status' AND UPPER(p_sort_dir) = 'DESC' THEN status END DESC
    LIMIT p_limit OFFSET p_offset;
END //

-- Approve New Request
CREATE PROCEDURE sp_admin_approve_requested(
    IN p_id INT
)
BEGIN
    UPDATE Users
    SET status = 'active'
        WHERE id = p_id
        AND status = 'requested';
END //

-- Deny New Request
CREATE PROCEDURE sp_admin_deny_requested(
    IN p_id INT
)
BEGIN
    DELETE FROM Users
        WHERE id = p_id
        AND status = 'requested';
END //

-- Get All User Details
CREATE PROCEDURE sp_admin_get_user_details(
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
        created_at
    FROM Users
    WHERE id = p_id;
END //

-- Suspend User
CREATE PROCEDURE sp_admin_suspend_user(IN p_id INT, IN p_hours INT)
BEGIN
    UPDATE Users 
    SET status = 'suspended', 
        suspended_until = DATE_ADD(NOW(), INTERVAL p_hours HOUR)
    WHERE id = p_id;
END //

-- Ban User
CREATE PROCEDURE sp_admin_ban_user(IN p_id INT)
BEGIN
    UPDATE Users 
    SET status = 'banned', 
        suspended_until = NULL 
    WHERE id = p_id;
END //

--  Reinstate User
CREATE PROCEDURE sp_admin_reinstate_user(IN p_id INT)
BEGIN
    UPDATE Users 
    SET status = 'active', 
        suspended_until = NULL 
    WHERE id = p_id;
END //

-- Delete User
CREATE PROCEDURE sp_admin_delete_user(IN p_id INT)
BEGIN
    DELETE FROM Users WHERE id = p_id;
END //

-- Reset Password
CREATE PROCEDURE sp_admin_reset_password(IN p_id INT, IN p_hash VARCHAR(255))
BEGIN
    UPDATE Users
    SET password_hash = p_hash
    WHERE id = p_id;
END //

DELIMITER ;