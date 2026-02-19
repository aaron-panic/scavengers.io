-- 08_reports_admin.sql - Administrative stored procedures for Tickets tables ('admin')
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

-- sp_admin_fetch_tickets(p_ticket_type, p_status, p_assigned_admin_u_id, p_tag_name, p_limit, p_offset)
-- ----------------------------------------------------------------------------
-- Desc:
--      Fetch active tickets with optional filtering for admin workflows.

CREATE PROCEDURE sp_admin_fetch_tickets(
    IN p_ticket_type VARCHAR(20),
    IN p_status VARCHAR(20),
    IN p_assigned_admin_u_id INT,
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
        t.status,
        t.priority,
        t.created_at,
        t.updated_at,
        u.username AS created_by_username,
        COUNT(*) OVER() AS total_records
    FROM Tickets t
    JOIN Users u ON t.u_id = u.id
    WHERE t.is_deleted = FALSE
        AND (p_ticket_type IS NULL OR p_ticket_type = '' OR t.ticket_type = p_ticket_type)
        AND (p_status IS NULL OR p_status = '' OR t.status = p_status)
        AND (
            p_assigned_admin_u_id IS NULL
            OR EXISTS (
                SELECT 1
                FROM TicketAssignments ta
                WHERE ta.ticket_id = t.id
                    AND ta.assigned_admin_u_id = p_assigned_admin_u_id
                    AND ta.is_deleted = FALSE
            )
        )
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



-- sp_admin_fetch_ticket(p_id)
-- ----------------------------------------------------------------------------
-- Desc:
--      Fetch full details for a single active ticket.

CREATE PROCEDURE sp_admin_fetch_ticket(
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
        u.username
    FROM Tickets t
    JOIN Users u ON t.u_id = u.id
    WHERE t.id = p_id
        AND t.is_deleted = FALSE;

END //



-- sp_admin_update_ticket(p_id, p_status, p_priority)
-- ----------------------------------------------------------------------------
-- Desc:
--      Update status and/or priority for a ticket.

CREATE PROCEDURE sp_admin_update_ticket(
    IN p_id INT,
    IN p_status VARCHAR(20),
    IN p_priority VARCHAR(20)
)
BEGIN

    UPDATE Tickets
    SET status = COALESCE(p_status, status),
        priority = COALESCE(p_priority, priority)
    WHERE id = p_id
        AND is_deleted = FALSE;

END //



-- sp_admin_create_ticket_status_message(p_ticket_id, p_changed_by_u_id, p_old_status, p_new_status, p_status_message)
-- ----------------------------------------------------------------------------
-- Desc:
--      Add a status history message entry for a ticket.

CREATE PROCEDURE sp_admin_create_ticket_status_message(
    IN p_ticket_id INT,
    IN p_changed_by_u_id INT,
    IN p_old_status VARCHAR(20),
    IN p_new_status VARCHAR(20),
    IN p_status_message TEXT
)
BEGIN

    INSERT INTO TicketStatusMessages (
        ticket_id,
        changed_by_u_id,
        old_status,
        new_status,
        status_message
    )
    VALUES (
        p_ticket_id,
        p_changed_by_u_id,
        p_old_status,
        p_new_status,
        p_status_message
    );

END //



-- sp_admin_update_ticket_status_message(p_id, p_old_status, p_new_status, p_status_message)
-- ----------------------------------------------------------------------------
-- Desc:
--      Update an existing status history message entry.

CREATE PROCEDURE sp_admin_update_ticket_status_message(
    IN p_id INT,
    IN p_old_status VARCHAR(20),
    IN p_new_status VARCHAR(20),
    IN p_status_message TEXT
)
BEGIN

    UPDATE TicketStatusMessages
    SET old_status = COALESCE(p_old_status, old_status),
        new_status = COALESCE(p_new_status, new_status),
        status_message = COALESCE(p_status_message, status_message)
     WHERE id = p_id
        AND is_deleted = FALSE;

END //



-- sp_admin_delete_ticket_status_message(p_id)
-- ----------------------------------------------------------------------------
-- Desc:
--      Soft delete a status history message entry.

CREATE PROCEDURE sp_admin_delete_ticket_status_message(
    IN p_id INT
)
BEGIN

     UPDATE TicketStatusMessages
    SET is_deleted = TRUE,
        deleted_at = CURRENT_TIMESTAMP
    WHERE id = p_id
      AND is_deleted = FALSE;

END //



-- sp_admin_create_ticket_tag(p_name)
-- ----------------------------------------------------------------------------
-- Desc:
--      Create a new tag.

CREATE PROCEDURE sp_admin_create_ticket_tag(
    IN p_name VARCHAR(64)
)
BEGIN

    INSERT INTO TicketTags (name)
    VALUES (p_name)
    ON DUPLICATE KEY UPDATE
        is_deleted = FALSE,
        deleted_at = NULL,
        updated_at = CURRENT_TIMESTAMP;

END //



-- sp_admin_link_ticket_tag(p_ticket_id, p_tag_id)
-- ----------------------------------------------------------------------------
-- Desc:
--      Link a tag to a ticket.

CREATE PROCEDURE sp_admin_link_ticket_tag(
    IN p_ticket_id INT,
    IN p_tag_id INT
)
BEGIN

    INSERT INTO TicketTagLinks (
        ticket_id,
        tag_id
    )
    VALUES (
        p_ticket_id,
        p_tag_id
    )
    ON DUPLICATE KEY UPDATE
        is_deleted = FALSE,
        deleted_at = NULL,
        updated_at = CURRENT_TIMESTAMP;

END //



-- sp_admin_unlink_ticket_tag(p_ticket_id, p_tag_id)
-- ----------------------------------------------------------------------------
-- Desc:
--      Soft delete a ticket/tag relationship.

CREATE PROCEDURE sp_admin_unlink_ticket_tag(
    IN p_ticket_id INT,
    IN p_tag_id INT
)
BEGIN

    UPDATE TicketTagLinks
    SET is_deleted = TRUE,
        deleted_at = CURRENT_TIMESTAMP
    WHERE ticket_id = p_ticket_id
      AND tag_id = p_tag_id
      AND is_deleted = FALSE;

END //



-- sp_admin_assign_ticket(p_ticket_id, p_assigned_admin_u_id, p_assigned_by_u_id)
-- ----------------------------------------------------------------------------
-- Desc:
--      Assign an admin to a ticket.

CREATE PROCEDURE sp_admin_assign_ticket(
    IN p_ticket_id INT,
    IN p_assigned_admin_u_id INT,
    IN p_assigned_by_u_id INT
)
BEGIN

    INSERT INTO TicketAssignments (
        ticket_id,
        assigned_admin_u_id,
        assigned_by_u_id
    )
    VALUES (
        p_ticket_id,
        p_assigned_admin_u_id,
        p_assigned_by_u_id
    )
    ON DUPLICATE KEY UPDATE
        is_deleted = FALSE,
        deleted_at = NULL,
        assigned_by_u_id = p_assigned_by_u_id,
        updated_at = CURRENT_TIMESTAMP;

END //



-- sp_admin_unassign_ticket(p_ticket_id, p_assigned_admin_u_id)
-- ----------------------------------------------------------------------------
-- Desc:
--      Soft remove an admin assignment from a ticket.

CREATE PROCEDURE sp_admin_unassign_ticket(
    IN p_ticket_id INT,
    IN p_assigned_admin_u_id INT
)
BEGIN

    UPDATE TicketAssignments
    SET is_deleted = TRUE,
        deleted_at = CURRENT_TIMESTAMP
    WHERE ticket_id = p_ticket_id
      AND assigned_admin_u_id = p_assigned_admin_u_id
      AND is_deleted = FALSE;

END //



-- sp_admin_fetch_ticket_assignments(p_ticket_id)
-- ----------------------------------------------------------------------------
-- Desc:
--      Fetch active admin assignments for a ticket.

CREATE PROCEDURE sp_admin_fetch_ticket_assignments(
    IN p_ticket_id INT
)
BEGIN

    SELECT
        ta.id,
        ta.ticket_id,
        ta.assigned_admin_u_id,
        ua.username AS assigned_admin_username,
        ta.assigned_by_u_id,
        ub.username AS assigned_by_username,
        ta.created_at,
        ta.updated_at
    FROM TicketAssignments ta
    JOIN Users ua ON ta.assigned_admin_u_id = ua.id
    LEFT JOIN Users ub ON ta.assigned_by_u_id = ub.id
    WHERE ta.ticket_id = p_ticket_id
      AND ta.is_deleted = FALSE
    ORDER BY ta.created_at DESC;

END //



-- sp_admin_delete_ticket(p_id)
-- ----------------------------------------------------------------------------
-- Desc:
--      Soft delete a ticket.

CREATE PROCEDURE sp_admin_delete_ticket(
    IN p_id INT
)
BEGIN

    UPDATE Tickets
    SET is_deleted = TRUE,
        deleted_at = CURRENT_TIMESTAMP
    WHERE id = p_id
      AND is_deleted = FALSE;

END //

DELIMITER ;