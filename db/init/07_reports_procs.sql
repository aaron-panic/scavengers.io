-- 07_reports_procs.sql - Stored procedures for Reports table ('user', 'social')
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

-- sp_create_report(p_u_id, p_target, p_description)
-- ----------------------------------------------------------------------------
-- Desc:
--      Submit a new issue or report.
-- Params:
--      p_u_id (INT)                    User id (matches Users.id)
--      p_target (VARCHAR 255)          Item being reported
--      p_description (TEXT)            Description of the issue

CREATE PROCEDURE sp_create_report(
    IN p_u_id INT,
    IN p_target VARCHAR(255),
    IN p_description TEXT
)
BEGIN

    INSERT INTO Reports (
        u_id,
        target,
        description
    )
    VALUES (
        p_u_id,
        p_target,
        p_description
    );

END //

DELIMITER ;