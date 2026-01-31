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