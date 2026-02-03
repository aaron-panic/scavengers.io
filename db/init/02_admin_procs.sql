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
CREATE PROCEDURE sp_admin_list_users()
BEGIN
    -- Remove suspensions if expired
    UPDATE Users
    SET status = 'active', suspended_until = NULL
    WHERE status = 'suspended'
        AND suspended_until <= NOW();

    -- Get user data
    SELECT
        id,
        username,
        email,
        role,
        status,
        suspended_until,
        created_at
    FROM Users
    ORDER BY created_at DESC;
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