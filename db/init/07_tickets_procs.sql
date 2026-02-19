-- 07_reports_procs.sql - Stored procedures for Tickets table ('user')
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



DELIMITER //

-- sp_create_ticket(p_u_id, p_ticket_type, p_title, p_description, p_priority)
-- ----------------------------------------------------------------------------
-- Desc:
--      Submit a new request or report ticket.

CREATE PROCEDURE sp_create_ticket(
    IN p_u_id INT,
    IN p_ticket_type VARCHAR(20),
    IN p_title VARCHAR(255),
    IN p_description TEXT,
    IN p_priority VARCHAR(20)
)
BEGIN

    INSERT INTO Tickets (
        u_id,
        ticket_type,
        title,
        description,
        priority
    )
    VALUES (
        p_u_id,
        p_ticket_type,
        p_title,
        p_description,
        COALESCE(p_priority, 'medium')
    );

END //



-- sp_fetch_tickets(p_ticket_type, p_status, p_tag_name, p_limit, p_offset)
-- ----------------------------------------------------------------------------
-- Desc:
--      Fetch active tickets with optional filtering by type, status, and tag.

CREATE PROCEDURE sp_fetch_tickets(
    IN p_ticket_type VARCHAR(20),
    IN p_status VARCHAR(20),
    IN p_tag_name VARCHAR(64),
    IN p_limit INT,
    IN p_offset INT
)
BEGIN

    IF p_limit > 100 THEN
        SET p_limit = 100;
    END IF;
    IF p_limit <= 0 THEN
        SET p_limit = 25;
    END IF;

    SELECT
        t.id,
        t.ticket_type,
        t.title,
        t.description,
        t.status,
        t.priority,
        t.created_at,
        t.updated_at,
        u.username,
        COUNT(*) OVER() AS total_records
    FROM Tickets t
    JOIN Users u ON t.u_id = u.id
    WHERE t.is_deleted = FALSE
      AND (p_ticket_type IS NULL OR p_ticket_type = '' OR t.ticket_type = p_ticket_type)
      AND (p_status IS NULL OR p_status = '' OR t.status = p_status)
      AND (
            p_tag_name IS NULL
            OR p_tag_name = ''
            OR EXISTS (
                SELECT 1
                FROM TicketTagLinks ttl
                JOIN TicketTags tt ON ttl.tag_id = tt.id
                WHERE ttl.ticket_id = t.id
                  AND ttl.is_deleted = FALSE
                  AND tt.is_deleted = FALSE
                  AND tt.name = p_tag_name
            )
        )
    ORDER BY t.created_at DESC
    LIMIT p_limit OFFSET p_offset;

END //



-- sp_fetch_tickets_by_user(p_u_id, p_ticket_type, p_status, p_tag_name, p_limit, p_offset)
-- ----------------------------------------------------------------------------
-- Desc:
--      Fetch active tickets submitted by a specific user with optional filters.

CREATE PROCEDURE sp_fetch_tickets_by_user(
    IN p_u_id INT,
    IN p_ticket_type VARCHAR(20),
    IN p_status VARCHAR(20),
    IN p_tag_name VARCHAR(64),
    IN p_limit INT,
    IN p_offset INT
)
BEGIN

    IF p_limit > 100 THEN
        SET p_limit = 100;
    END IF;
    IF p_limit <= 0 THEN
        SET p_limit = 25;
    END IF;

    SELECT
        t.id,
        t.ticket_type,
        t.title,
        t.description,
        t.status,
        t.priority,
        t.created_at,
        t.updated_at,
        COUNT(*) OVER() AS total_records
    FROM Tickets t
    WHERE t.is_deleted = FALSE
      AND t.u_id = p_u_id
      AND (p_ticket_type IS NULL OR p_ticket_type = '' OR t.ticket_type = p_ticket_type)
      AND (p_status IS NULL OR p_status = '' OR t.status = p_status)
      AND (
            p_tag_name IS NULL
            OR p_tag_name = ''
            OR EXISTS (
                SELECT 1
                FROM TicketTagLinks ttl
                JOIN TicketTags tt ON ttl.tag_id = tt.id
                WHERE ttl.ticket_id = t.id
                  AND ttl.is_deleted = FALSE
                  AND tt.is_deleted = FALSE
                  AND tt.name = p_tag_name
            )
        )
    ORDER BY t.created_at DESC
    LIMIT p_limit OFFSET p_offset;

END //



-- sp_fetch_ticket(p_id)
-- ----------------------------------------------------------------------------
-- Desc:
--      Fetch full details for a single ticket.

CREATE PROCEDURE sp_fetch_ticket(
    IN p_id INT
)
BEGIN

    SELECT
        t.id,
        t.u_id,
        t.ticket_type,
        t.title,
        t.description,
        t.status,
        t.priority,
        t.created_at,
        t.updated_at,
        u.username,
        u.email
    FROM Tickets t
    JOIN Users u ON t.u_id = u.id
    WHERE t.id = p_id
      AND t.is_deleted = FALSE;

END //



-- sp_fetch_ticket_status_messages(p_ticket_id)
-- ----------------------------------------------------------------------------
-- Desc:
--      Fetch active status message history for a ticket.

CREATE PROCEDURE sp_fetch_ticket_status_messages(
    IN p_ticket_id INT
)
BEGIN

    SELECT
        tsm.id,
        tsm.ticket_id,
        tsm.old_status,
        tsm.new_status,
        tsm.status_message,
        tsm.created_at,
        u.username AS changed_by_username
    FROM TicketStatusMessages tsm
    JOIN Users u ON tsm.changed_by_u_id = u.id
    WHERE tsm.ticket_id = p_ticket_id
      AND tsm.is_deleted = FALSE
    ORDER BY tsm.created_at DESC;

END //



-- sp_fetch_ticket_tags(p_ticket_id)
-- ----------------------------------------------------------------------------
-- Desc:
--      Fetch active tag list for a ticket.

CREATE PROCEDURE sp_fetch_ticket_tags(
    IN p_ticket_id INT
)
BEGIN

    SELECT
        tt.id,
        tt.name
    FROM TicketTagLinks ttl
    JOIN TicketTags tt ON ttl.tag_id = tt.id
    WHERE ttl.ticket_id = p_ticket_id
      AND ttl.is_deleted = FALSE
      AND tt.is_deleted = FALSE
    ORDER BY tt.name ASC;

END //

DELIMITER ;