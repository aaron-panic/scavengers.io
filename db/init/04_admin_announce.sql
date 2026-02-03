-- 04_admin_announce.sql - Stored procedures for admin announcement management
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

-- Create Announcement
CREATE PROCEDURE sp_admin_create_announcement(
    IN p_uid INT,
    IN p_title VARCHAR(255),
    IN p_subtitle VARCHAR(255),
    IN p_content TEXT,
    IN p_footnote TEXT
)
BEGIN
    INSERT INTO Announcements (u_id, title, subtitle, content, footnote)
    VALUES (p_uid, p_title, p_subtitle, p_content, p_footnote);
END //

-- Update Announcement
CREATE PROCEDURE sp_admin_update_announcement(
    IN p_id INT,
    IN p_title VARCHAR(255),
    IN p_subtitle VARCHAR(255),
    IN p_content TEXT,
    IN p_footnote TEXT
)
BEGIN
    UPDATE Announcements
    SET title = p_title,
        subtitle = p_subtitle,
        content = p_content,
        footnote = p_footnote
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
    SELECT id, title, subtitle, content, footnote
    FROM Announcements
    WHERE id = p_id;
END //

-- List Announcements (Admin View - Paginated)
CREATE PROCEDURE sp_admin_list_announcements(
    IN p_limit INT,
    IN p_offset INT
)
BEGIN
    SELECT
        a.id,
        a.title,
        a.created_at,
        u.username,
        COUNT(*) OVER() as total_records
    FROM Announcements a
    JOIN Users u ON a.u_id = u.id
    ORDER BY a.created_at DESC
    LIMIT p_limit OFFSET p_offset;
END //

DELIMITER ;