-- 01_users_procs.sql - Stored procedures for Users table ('user', 'social')
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

-- sp_fetch_user_auth(p_username)
-- ----------------------------------------------------------------------------
-- Desc:
--      Retrieve password hash, role, and status for login authentication.
-- Params:
--      p_username (VARCHAR 50)         Username to fetch credentials for
-- Notes:
--      this runs status update for suspended users and updates record if the
--      suspension is expired. This is to allow users to login if the admin 
--      has not tripped the global update check.

CREATE PROCEDURE sp_fetch_user_auth(
    IN p_username VARCHAR(50)
)
BEGIN

    -- This is the status update from Notes above
    UPDATE Users
    SET status = 'active', suspended_until = NULL
    WHERE username = p_username
        AND status = 'suspended'
        AND suspended_until <= NOW();

    SELECT id, password_hash, role, status, suspended_until
    FROM Users
    WHERE username = p_username;

END //



-- sp_create_user_request(p_username, p_password_hash, p_email)
-- ----------------------------------------------------------------------------
-- Desc:
--      Submit a new user registration request.
-- Params:
--      p_username (VARCHAR 50)         Username requested to register
--      p_password_hash (VARCHAR 255)   Hashed password provided
--      p_email (VARCHAR 100)           Email to associate with the account
-- Notes:
--      This may fail if the username already exists in the database. Failure
--      logic is handled in the python script calling.

CREATE PROCEDURE sp_create_user_request(
    IN p_username VARCHAR(50),
    IN p_password_hash VARCHAR(255),
    IN p_email VARCHAR(100)
)
BEGIN

    INSERT INTO Users (
        username,
        password_hash,
        email,
        role,
        status
    )
    VALUES (
        p_username,
        p_password_hash,
        p_email,
        'social',
        'requested'
    );
    
END //

DELIMITER ;