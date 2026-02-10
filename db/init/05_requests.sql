-- 05_requests.sql - Table and retrieval stored procedure for requests
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

CREATE TABLE IF NOT EXISTS Requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    u_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status ENUM('Pending', 'In_Progress', 'Completed', 'Rejected') NOT NULL DEFAULT 'Pending',
    status_message TEXT,
    ref_1 VARCHAR(255),
    ref_2 VARCHAR(255),
    ref_3 VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_req_u_id
        FOREIGN KEY (u_id)
        REFERENCES Users (id)
        ON DELETE CASCADE
);

DELIMITER //

-- ---------------------------------------------------------
-- User Procedures
-- ---------------------------------------------------------

-- Create Request
CREATE PROCEDURE sp_create_request(
    IN p_u_id INT,
    IN p_title VARCHAR(255),
    IN p_description TEXT,
    IN p_ref_1 VARCHAR(255),
    IN p_ref_2 VARCHAR(255),
    IN p_ref_3 VARCHAR(255)
)
BEGIN
    INSERT INTO Requests (u_id, title, description, ref_1, ref_2, ref_3)
    VALUES (p_u_id, p_title, p_description, p_ref_1, p_ref_2, p_ref_3);
END //

-- List Requests by User
CREATE PROCEDURE sp_list_requests_by_user(
    IN p_u_id INT,
    IN p_limit INT,
    IN p_offset INT
)
BEGIN
    SELECT
        id,
        title,
        status,
        created_at,
        COUNT(*) OVER() as total_records
    FROM Requests
    WHERE u_id = p_u_id
    ORDER BY created_at DESC
    LIMIT p_limit OFFSET p_offset;
END //

-- List Requests by Status (Public/User View)
CREATE PROCEDURE sp_list_requests_by_status(
    IN p_status VARCHAR(20),
    IN p_limit INT,
    IN p_offset INT
)
BEGIN
    SELECT
        r.id,
        r.title,
        r.status,
        r.created_at,
        u.username,
        COUNT(*) OVER() as total_records
    FROM Requests r
    JOIN Users u ON r.u_id = u.id
    WHERE r.status = p_status
    ORDER BY r.created_at DESC
    LIMIT p_limit OFFSET p_offset;
END //

-- ---------------------------------------------------------
-- Admin Procedures
-- ---------------------------------------------------------

-- List All Requests (Admin View - Sortable)
CREATE PROCEDURE sp_admin_list_requests(
    IN p_limit INT,
    IN p_offset INT,
    IN p_sort_col VARCHAR(20),
    IN p_sort_dir VARCHAR(4)
)
BEGIN
    SELECT
        r.id,
        r.title,
        r.status,
        r.created_at,
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

-- Get Single Request Details (Admin Modal)
CREATE PROCEDURE sp_admin_get_request(
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
        u.username,
        u.email
    FROM Requests r
    JOIN Users u ON r.u_id = u.id
    WHERE r.id = p_id;
END //

-- Update Request Status & Message
CREATE PROCEDURE sp_admin_update_request(
    IN p_id INT,
    IN p_status VARCHAR(20),
    IN p_message TEXT
)
BEGIN
    UPDATE Requests
    SET status = COALESCE(p_status, status),
        status_message = COALESCE(p_message, status_message)
    WHERE id = p_id;
END //

-- Delete Request
CREATE PROCEDURE sp_admin_delete_request(
    IN p_id INT
)
BEGIN
    DELETE FROM Requests WHERE id = p_id;
END //

DELIMITER ;