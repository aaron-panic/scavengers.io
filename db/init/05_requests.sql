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
    ref_1 TEXT,
    ref_2 TEXT,
    ref_3 TEXT,
    status ENUM('Pending', 'In_Progress', 'Completed', 'Rejected') NOT NULL DEFAULT 'Pending',
    status_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_req_u_id
        FOREIGN KEY (u_id)
        REFERENCES Users (id)
        ON DELETE CASCADE
);

DELIMITER //

-- Fetch requests by status, supports pagination
CREATE PROCEDURE sp_get_requests_by_status(
    IN p_status VARCHAR(20),
    IN p_limit INT,
    IN p_offset INT
)
BEGIN
    SELECT
        r.id,
        r.title,
        r.description,
        r.ref_1,
        r.ref_2,
        r.ref_3,
        r.status,
        r.status_message,
        r.created_at,
        u.username
    FROM Requests r
    JOIN Users u ON r.u_id = u.id
    WHERE 
        (p_status = 'all' OR r.status = p_status)
    ORDER BY r.created_at DESC
    LIMIT p_limit OFFSET p_offset;
END //

CREATE PROCEDURE sp_get_requests_by_uid(
    IN p_u_id INT,
    IN p_limit INT,
    IN p_offset INT
)
BEGIN
    SELECT
        r.id,
        r.title,
        r.description,
        r.ref_1,
        r.ref_2,
        r.ref_3,
        r.status,
        r.status_message,
        r.created_at,
        u.username
    FROM Requests r
    JOIN Users u ON r.u_id = u.id
    WHERE (r.u_id = p_u_id)
    ORDER BY r.created_at DESC
    LIMIT p_limit OFFSET p_offset;
END //

-- Create a new request (User)
CREATE PROCEDURE sp_create_request(
    IN p_u_id INT,
    IN p_title VARCHAR(255),
    IN p_description TEXT,
    IN p_ref_1 TEXT,
    IN p_ref_2 TEXT,
    IN p_ref_3 TEXT
)
BEGIN
    INSERT INTO Requests (u_id, title, description, ref_1, ref_2, ref_3)
    VALUES (p_u_id, p_title, p_description, p_ref_1, p_ref_2, p_ref_3);
END //

-- Update Request (Admin)
CREATE PROCEDURE sp_admin_update_request(
    IN p_req_id INT,
    IN p_status VARCHAR(20),
    IN p_status_message TEXT
)
BEGIN
    UPDATE Requests 
    SET 
        status = COALESCE(p_status, status),
        status_message = COALESCE(p_status_message, status_message)
    WHERE id = p_req_id;
END //

-- Delete request (Admin)
CREATE PROCEDURE sp_admin_delete_request(
    IN p_req_id INT
)
BEGIN
    DELETE FROM Requests WHERE id = p_req_id;
END //

DELIMITER ;