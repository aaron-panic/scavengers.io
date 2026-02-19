-- 06_reports_table.sql - Generate Tickets and related tables
-- Copyright (C) 2026 Aaron Reichenbach
--
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU Affero General Public License as
-- published by the Free Software Foundation, either version 3 of the
-- License, or (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU Affero General Public License for more details.
--
-- You should have received a copy of the GNU Affero General Public License
-- along with this program.  If not, see <https://www.gnu.org/licenses/>.



-- Tickets Tables
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    u_id INT NOT NULL,
    ticket_type ENUM('request', 'report') NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status ENUM(
        'pending',
        'in progress',
        'completed',
        'rejected',
        'open',
        'closed',
        'wontfix'
    ) NOT NULL DEFAULT 'pending',
    priority ENUM('very low', 'low', 'medium', 'high', 'very high') NOT NULL DEFAULT 'medium',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    CONSTRAINT fk_tickets_u_id
        FOREIGN KEY (u_id)
        REFERENCES Users (id)
         ON DELETE CASCADE,
    INDEX idx_tickets_u_id (u_id),
    INDEX idx_tickets_type_status (ticket_type, status),
    INDEX idx_tickets_priority (priority),
    INDEX idx_tickets_deleted (is_deleted)
);

CREATE TABLE IF NOT EXISTS TicketTags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_tickettags_name (name),
    INDEX idx_tickettags_deleted (is_deleted)
);


CREATE TABLE IF NOT EXISTS TicketTagLinks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    tag_id INT NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_tickettaglinks_ticket_id
        FOREIGN KEY (ticket_id)
        REFERENCES Tickets (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_tickettaglinks_tag_id
        FOREIGN KEY (tag_id)
        REFERENCES TicketTags (id)
        ON DELETE CASCADE,
    UNIQUE KEY uq_tickettaglinks_ticket_tag (ticket_id, tag_id),
    INDEX idx_tickettaglinks_ticket (ticket_id, is_deleted),
    INDEX idx_tickettaglinks_tag (tag_id, is_deleted)
);


CREATE TABLE IF NOT EXISTS TicketAssignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    assigned_admin_u_id INT NOT NULL,
    assigned_by_u_id INT,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_ticketassignments_ticket_id
        FOREIGN KEY (ticket_id)
        REFERENCES Tickets (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_ticketassignments_assigned_admin_u_id
        FOREIGN KEY (assigned_admin_u_id)
        REFERENCES Users (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_ticketassignments_assigned_by_u_id
        FOREIGN KEY (assigned_by_u_id)
        REFERENCES Users (id)
        ON DELETE SET NULL,
    UNIQUE KEY uq_ticketassignments_ticket_admin (ticket_id, assigned_admin_u_id),
    INDEX idx_ticketassignments_ticket (ticket_id, is_deleted),
    INDEX idx_ticketassignments_admin (assigned_admin_u_id, is_deleted)
);


CREATE TABLE IF NOT EXISTS TicketStatusMessages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    changed_by_u_id INT NOT NULL,
    old_status ENUM(
        'pending',
        'in progress',
        'completed',
        'rejected',
        'open',
        'closed',
        'wontfix'
    ),
    new_status ENUM(
        'pending',
        'in progress',
        'completed',
        'rejected',
        'open',
        'closed',
        'wontfix'
    ) NOT NULL,
    status_message TEXT,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_ticketstatusmessages_ticket_id
        FOREIGN KEY (ticket_id)
        REFERENCES Tickets (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_ticketstatusmessages_changed_by_u_id
        FOREIGN KEY (changed_by_u_id)
        REFERENCES Users (id)
        ON DELETE CASCADE,
    INDEX idx_ticketstatusmessages_ticket (ticket_id, is_deleted),
    INDEX idx_ticketstatusmessages_changed_by (changed_by_u_id)
);

