-- 11_requests_admin.sql - Stored procedures for Requests table ('admin')
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

-- sp_admin_fetch_requests(p_limit, p_offset, p_sort_col, p_sort_dir)
-- ----------------------------------------------------------------------------
-- Desc:
--      Fetch a paginated list of all requests.
-- Params:
--      p_limit (INT)                   Number of records to retrieve for a page view
--      p_offset (INT)                  Where to start retrieving records for page view
--      p_sort_col (VARCHAR 20)         Column to sort by
--      p_sort_dir (VARCHAR 4)          Direction (ASC or DESC) to sort

CREATE PROCEDURE sp_admin_fetch_requests(
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
    ORDER BY
        CASE WHEN p_sort_col = 'id' AND UPPER(p_sort_dir) = 'ASC' THEN r.id END ASC,
        CASE WHEN p_sort_col = 'id' AND UPPER(p_sort_dir) = 'DESC' THEN r.id END DESC,
        
        CASE WHEN p_sort_col = 'title' AND UPPER(p_sort_dir) = 'ASC' THEN r.title END ASC,
        CASE WHEN p_sort_col = 'title' AND UPPER(p_sort_dir) = 'DESC' THEN r.title END DESC,

        CASE WHEN p_sort_col = 'status' AND UPPER(p_sort_dir) = 'ASC' THEN r.status END ASC,
        CASE WHEN p_sort_col = 'status' AND UPPER(p_sort_dir) = 'DESC' THEN r.status END DESC,

        CASE WHEN p_sort_col = 'username' AND UPPER(p_sort_dir) = 'ASC' THEN u.username END ASC,
        CASE WHEN p_sort_col = 'username' AND UPPER(p_sort_dir) = 'DESC' THEN u.username END DESC,

        CASE WHEN p_sort_col = 'created_at' AND UPPER(p_sort_dir) = 'ASC' THEN r.created_at END ASC,
        CASE WHEN p_sort_col = 'created_at' AND UPPER(p_sort_dir) = 'DESC' THEN r.created_at END DESC
    LIMIT p_limit OFFSET p_offset;

END //



-- sp_admin_fetch_request(p_id)
-- ----------------------------------------------------------------------------
-- Desc:
--      Fetch a specific request by id.
-- Params:
--      p_id (INT)                      Request id (matches Requests.id)

CREATE PROCEDURE sp_admin_fetch_request(
    IN p_id INT
)
BEGIN

    SELECT 
        r.id,
        r.title,
        r.description,
        r.status,
        r.status_message,
        r.ref_1,
        r.ref_2,
        r.ref_3,
        r.created_at,
        r.updated_at,
        u.username,
        u.email
    FROM Requests r
    JOIN Users u ON r.u_id = u.id
    WHERE r.id = p_id;

END //



-- sp_admin_update_request(p_id, p_status, p_status_message)
-- ----------------------------------------------------------------------------
-- Desc:
--      Update request status and status message.
-- Params:
--      p_id (INT)                      Request id (matches Requests.id)
--      p_status (VARCHAR 20)           New status to update or NULL for no change
--      p_status_message (TEXT)         New message to update or NULL for no change

CREATE PROCEDURE sp_admin_update_request(
    IN p_id INT,
    IN p_status VARCHAR(20),
    IN p_status_message TEXT
)
BEGIN

    UPDATE Requests
    SET status = COALESCE(p_status, status),
        status_message = COALESCE(p_status_message, status_message)
    WHERE id = p_id;

END //



-- sp_admin_delete_request(p_id)
-- ----------------------------------------------------------------------------
-- Desc:
--      Permanently delete a request.
-- Params:
--      p_id (INT)                      Request id (matches Requests.id)

CREATE PROCEDURE sp_admin_delete_request(
    IN p_id INT
)
BEGIN
    DELETE FROM Requests WHERE id = p_id;
END //

DELIMITER ;