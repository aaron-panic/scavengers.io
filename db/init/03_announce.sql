-- 03_announce.sql - Create announcements table and stored procedures for access
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

-- Announce Table
CREATE TABLE IF NOT EXISTS Announcements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    u_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    title VARCHAR(255) NOT NULL,
    subtitle VARCHAR(255),
    content TEXT NOT NULL,
    footnote TEXT,
    is_visible BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_u_id
        FOREIGN KEY (u_id)
        REFERENCES Users (id)
        ON DELETE CASCADE
);

DELIMITER //

-- Fetch Announcements
CREATE PROCEDURE sp_get_announcements()
BEGIN
    SELECT
        a.id,
        a.title,
        a.subtitle,
        a.content,
        a.footnote,
        a.created_at,
        u.username
    FROM Announcements a
    JOIN Users u ON a.u_id = u.id
    WHERE a.is_visible = TRUE
    ORDER BY a.created_at DESC
    LIMIT 25;
END //

-- ADMIN PROCS

-- Create Announcement
CREATE PROCEDURE sp_admin_create_announcement(
    IN p_uid INT,
    IN p_title VARCHAR(255),
    IN p_subtitle VARCHAR(255),
    IN p_content TEXT,
    IN p_footnote TEXT,
    IN p_is_visible BOOLEAN
)
BEGIN
    INSERT INTO Announcements (u_id, title, subtitle, content, footnote, is_visible)
    VALUES (p_uid, p_title, p_subtitle, p_content, p_footnote, p_is_visible);
END //

-- Update Announcement
CREATE PROCEDURE sp_admin_update_announcement(
    IN p_id INT,
    IN p_title VARCHAR(255),
    IN p_subtitle VARCHAR(255),
    IN p_content TEXT,
    IN p_footnote TEXT,
    IN p_is_visible BOOLEAN
)
BEGIN
    UPDATE Announcements
    SET title = p_title,
        subtitle = p_subtitle,
        content = p_content,
        footnote = p_footnote,
        is_visible = p_is_visible
    WHERE id = p_id;
END //

-- Delete Announcement
CREATE PROCEDURE sp_admin_delete_announcement(
    IN p_id INT
)
BEGIN
    DELETE FROM Announcements WHERE id = p_id;
END //

-- Get Single Announcement (For Editing)
CREATE PROCEDURE sp_admin_get_announcement(
    IN p_id INT
)
BEGIN
    SELECT id, title, subtitle, content, footnote, is_visible
    FROM Announcements
    WHERE id = p_id;
END //

-- List Announcements (Admin View)
CREATE PROCEDURE sp_admin_list_announcements(
    IN p_limit INT,
    IN p_offset INT,
    IN p_sort_col VARCHAR(20),
    IN p_sort_dir VARCHAR(4)
)
BEGIN
    SELECT
        a.id,
        a.title,
        a.created_at,
        a.is_visible,
        u.username,
        COUNT(*) OVER() as total_records
    FROM Announcements a
    JOIN Users u ON a.u_id = u.id
    ORDER BY
        CASE WHEN p_sort_col = 'id' AND UPPER(p_sort_dir) = 'ASC' THEN a.id END ASC,
        CASE WHEN p_sort_col = 'id' AND UPPER(p_sort_dir) = 'DESC' THEN a.id END DESC,
        
        CASE WHEN p_sort_col = 'title' AND UPPER(p_sort_dir) = 'ASC' THEN a.title END ASC,
        CASE WHEN p_sort_col = 'title' AND UPPER(p_sort_dir) = 'DESC' THEN a.title END DESC,

        CASE WHEN p_sort_col = 'created_at' AND UPPER(p_sort_dir) = 'ASC' THEN a.created_at END ASC,
        CASE WHEN p_sort_col = 'created_at' AND UPPER(p_sort_dir) = 'DESC' THEN a.created_at END DESC,

        CASE WHEN p_sort_col = 'username' AND UPPER(p_sort_dir) = 'ASC' THEN u.username END ASC,
        CASE WHEN p_sort_col = 'username' AND UPPER(p_sort_dir) = 'DESC' THEN u.username END DESC
    LIMIT p_limit OFFSET p_offset;
END //

DELIMITER ;