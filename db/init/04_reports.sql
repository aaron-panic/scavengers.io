-- 05_reports.sql - Table and retrieval stored procedure for reports
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

CREATE TABLE IF NOT EXISTS Reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    u_id INT NOT NULL,
    target VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status ENUM('open', 'resolved', 'wontfix') NOT NULL DEFAULT 'open',
    status_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rep_u_id
        FOREIGN KEY (u_id)
        REFERENCES Users (id)
        ON DELETE CASCADE
);

DELIMITER //

-- Create Report (User)
CREATE PROCEDURE sp_create_report(
    IN p_u_id INT,
    IN p_target VARCHAR(255),
    IN p_description TEXT
)
BEGIN
    INSERT INTO Reports (u_id, target, description)
    VALUES (p_u_id, p_target, p_description);
END //

-- List Reports (Admin) - Sortable with Pagination
CREATE PROCEDURE sp_admin_list_reports(
    IN p_limit INT,
    IN p_offset INT,
    IN p_sort_col VARCHAR(20),
    IN p_sort_dir VARCHAR(4)
)
BEGIN
    SELECT
        r.id,
        r.target,
        r.description,
        r.status,
        r.status_message,
        r.created_at,
        u.username,
        COUNT(*) OVER() as total_records
    FROM Reports r
    JOIN Users u ON r.u_id = u.id
    ORDER BY
        CASE WHEN p_sort_col = 'id' AND UPPER(p_sort_dir) = 'ASC' THEN r.id END ASC,
        CASE WHEN p_sort_col = 'id' AND UPPER(p_sort_dir) = 'DESC' THEN r.id END DESC,
        
        CASE WHEN p_sort_col = 'target' AND UPPER(p_sort_dir) = 'ASC' THEN r.target END ASC,
        CASE WHEN p_sort_col = 'target' AND UPPER(p_sort_dir) = 'DESC' THEN r.target END DESC,

        CASE WHEN p_sort_col = 'status' AND UPPER(p_sort_dir) = 'ASC' THEN r.status END ASC,
        CASE WHEN p_sort_col = 'status' AND UPPER(p_sort_dir) = 'DESC' THEN r.status END DESC,

        CASE WHEN p_sort_col = 'username' AND UPPER(p_sort_dir) = 'ASC' THEN u.username END ASC,
        CASE WHEN p_sort_col = 'username' AND UPPER(p_sort_dir) = 'DESC' THEN u.username END DESC,

        CASE WHEN p_sort_col = 'created_at' AND UPPER(p_sort_dir) = 'ASC' THEN r.created_at END ASC,
        CASE WHEN p_sort_col = 'created_at' AND UPPER(p_sort_dir) = 'DESC' THEN r.created_at END DESC
    LIMIT p_limit OFFSET p_offset;
END //

-- Get Single Report (Admin Modal)
CREATE PROCEDURE sp_admin_get_report(
    IN p_id INT
)
BEGIN
    SELECT 
        r.id,
        r.target,
        r.description,
        r.status,
        r.status_message,
        r.created_at,
        u.username,
        u.email
    FROM Reports r
    JOIN Users u ON r.u_id = u.id
    WHERE r.id = p_id;
END //

-- Update Report Status/Message (Admin)
CREATE PROCEDURE sp_admin_update_report(
    IN p_report_id INT,
    IN p_status VARCHAR(20),
    IN p_status_message TEXT
)
BEGIN
    UPDATE Reports
    SET 
        status = COALESCE(p_status, status),
        status_message = COALESCE(p_status_message, status_message)
    WHERE id = p_report_id;
END //

-- Delete Report (Admin)
CREATE PROCEDURE sp_admin_delete_report(
    IN p_report_id INT
)
BEGIN
    DELETE FROM Reports WHERE id = p_report_id;
END //

DELIMITER ;