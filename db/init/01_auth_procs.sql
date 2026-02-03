-- 01_auth_procs.sql - Stored procedures for authorization
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
