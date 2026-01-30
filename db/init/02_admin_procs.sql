-- Admin list users, removes suspensions if expired
DELIMITER //

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

DELIMITER ;
