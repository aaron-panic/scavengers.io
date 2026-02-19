-- 04_announcements_procs.sql - Stored procedures for Announcements table ('user', 'social')
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

-- sp_fetch_announcements()
-- ----------------------------------------------------------------------------
-- Desc:
--      Fetch the public feed of visible announcements.

CREATE PROCEDURE sp_fetch_announcements()
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