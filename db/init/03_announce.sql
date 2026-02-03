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

DELIMITER ;