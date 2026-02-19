-- 05_announcements_admin.sql - Stored procedures for Announcements table ('admin')
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

-- sp_admin_create_announcement(p_u_id, p_title, p_subtitle, p_content, p_footnote, p_is_visible)
-- ----------------------------------------------------------------------------
-- Desc:
--      Create a new announcement.

CREATE PROCEDURE sp_admin_create_announcement(
    IN p_u_id INT,
    IN p_title VARCHAR(255),
    IN p_subtitle VARCHAR(255),
    IN p_content TEXT,
    IN p_footnote TEXT,
    IN p_is_visible BOOLEAN
)
BEGIN

    INSERT INTO Announcements (
        u_id,
        title,
        subtitle,
        content,
        footnote,
        is_visible
    )
    VALUES (
        p_u_id,
        p_title,
        p_subtitle,
        p_content,
        p_footnote,
        p_is_visible
    );

END //



-- sp_admin_update_announcement(p_id, p_title, p_subtitle, p_content, p_footnote, p_is_visible)
-- ----------------------------------------------------------------------------
-- Desc:
--      Update an existing announcement.

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



-- sp_admin_delete_announcement(p_id)
-- ----------------------------------------------------------------------------
-- Desc:
--      Permanently delete an announcement.

CREATE PROCEDURE sp_admin_delete_announcement(
    IN p_id INT
)
BEGIN

    DELETE FROM Announcements WHERE id = p_id;

END //



-- sp_admin_fetch_announcement(p_id)
-- ----------------------------------------------------------------------------
-- Desc:
--      Fetch a single announcement by ID for editing.

CREATE PROCEDURE sp_admin_fetch_announcement(
    IN p_id INT
)
BEGIN

    SELECT
        id,
        title,
        subtitle,
        content,
        footnote,
        is_visible
    FROM Announcements
    WHERE id = p_id;

END //



-- sp_admin_fetch_announcements(p_limit, p_offset, p_sort_col, p_sort_dir)
-- ----------------------------------------------------------------------------
-- Desc:
--      Fetch a paginated list of all announcements (including hidden).

CREATE PROCEDURE sp_admin_fetch_announcements(
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
        a.id,
        a.title,
        a.created_at,
        a.updated_at,
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