-- 06_reports_table.sql - Generate Reports table
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



-- Reportss Table
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    u_id INT NOT NULL,
    target VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status ENUM('open', 'resolved', 'wontfix') NOT NULL DEFAULT 'open',
    status_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_report_u_id
        FOREIGN KEY (u_id)
        REFERENCES Users (id)
        ON DELETE CASCADE
);