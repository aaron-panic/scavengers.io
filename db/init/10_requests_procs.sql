-- 10_requests_procs.sql - Stored procedures for Requests table ('user', 'social')
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

-- sp_create_request(p_u_id, p_title, p_description, p_ref_1, p_ref_2, p_ref_3)
-- ----------------------------------------------------------------------------
-- Desc:
--      Create a new request for the website.
-- Params:
--      p_u_id (INT)                    User id (matches Users.id)
--      p_title (VARCHAR 255)           Title of the request
--      p_description (TEXT)            Description of the request
--      p_ref_1 (VARCHAR 255)           Link or other Reference (optional)
--      p_ref_2 (VARCHAR 255)           Link or other Reference (optional)
--      p_ref_3 (VARCHAR 255)           Link or other Reference (optional)

CREATE PROCEDURE sp_create_request(
    IN p_u_id INT,
    IN p_title VARCHAR(255),
    IN p_description TEXT,
    IN p_ref_1 VARCHAR(255),
    IN p_ref_2 VARCHAR(255),
    IN p_ref_3 VARCHAR(255)
)
BEGIN

    INSERT INTO Requests (
        u_id,
        title,
        description,
        ref_1,
        ref_2,
        ref_3
    )
    VALUES (
        p_u_id,
        p_title,
        p_description,
        p_ref_1,
        p_ref_2,
        p_ref_3
    );

END //



-- sp_fetch_requests_by_user(p_u_id, p_limit, p_offset)
-- ----------------------------------------------------------------------------
-- Desc:
--      Fetch requests submitted by a specific user.
-- Params:
--      p_u_id (INT)                    User id (matches Users.id)
--      p_limit (INT)                   Number of records to retrieve for a page view
--      p_offset (INT)                  Where to start retrieving records for page view

CREATE PROCEDURE sp_fetch_requests_by_user(
    IN p_u_id INT,
    IN p_limit INT,
    IN p_offset INT
)
BEGIN

    -- Hard caps to ensure that there's no nonsense from the caller
    IF p_limit > 50 THEN
        SET p_limit = 50;
    END IF;
    IF p_limit <= 0 THEN
        SET p_limit = 25;
    END IF;

    SELECT
        id,
        title,
        status,
        created_at,
        updated_at,
        COUNT(*) OVER() as total_records
    FROM Requests
    WHERE u_id = p_u_id
    ORDER BY created_at DESC
    LIMIT p_limit OFFSET p_offset;

END //



-- sp_fetch_requests_by_status(p_status, p_limit, p_offset)
-- ----------------------------------------------------------------------------
-- Desc:
--      Fetch requests filterd by status.
-- Params:
--      p_status (VARCHAR 20)           Status to filter by
--      p_limit (INT)                   Number of records to retrieve for a page view
--      p_offset (INT)                  Where to start retrieving records for page view

CREATE PROCEDURE sp_fetch_requests_by_status(
    IN p_status VARCHAR(20),
    IN p_limit INT,
    IN p_offset INT
)
BEGIN

    -- Hard caps to ensure that there's no nonsense from the caller
    IF p_limit > 50 THEN
        SET p_limit = 50;
    END IF;
    IF p_limit <= 0 THEN
        SET p_limit = 25;
    END IF;

    SELECT
        r.id,
        r.title,
        r.status,
        r.created_at,
        r.updated_at,
        u.username,
        COUNT(*) OVER() as total_records
    FROM Requests r
    JOIN Users u ON r.u_id = u.id
    WHERE r.status = p_status
    ORDER BY r.created_at DESC
    LIMIT p_limit OFFSET p_offset;
    
END //

DELIMITER ;