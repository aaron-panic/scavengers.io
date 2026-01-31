DELIMITER //

-- Login & Unsuspend (if suspension expired)
CREATE PROCEDURE sp_get_user_auth(IN p_username VARCHAR(50))
BEGIN
    UPDATE Users
    SET status = 'active', suspended_until = NULL
    WHERE username = p_username
        AND status = 'suspended'
        AND suspended_until <= NOW();

    SELECT password_hash, role, status, suspended_until
    FROM Users
    WHERE username = p_username;
END //

-- Registration Request (new user)
CREATE PROCEDURE sp_register_user(
    IN p_username VARCHAR(50),
    IN p_password_hash VARCHAR(255),
    IN p_email VARCHAR(100)
)
BEGIN
    INSERT INTO Users (username, password_hash, email, role, status)
    VALUES (p_username, p_password_hash, p_email, 'social', 'requested');
END //

DELIMITER ;
