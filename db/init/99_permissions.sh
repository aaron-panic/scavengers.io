# 99_permission.sh - Create user accounts for RBAC and grant permissions
# Copyright (C) 2026 Aaron Reichenbach
#
# This program is free software: you can redistribute it and/or modify         
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

#!/bin/bash
set -e

# Create Database Users and Assign Permissions
mariadb -u root -p"${MARIADB_ROOT_PASSWORD}" <<EOF



-- ----------------------------------------------------------------------------
-- MARIADB USER CREATION FOR RBAC                                             -
-- ----------------------------------------------------------------------------
-- NOTE: All access is controlled by stored procedures with no direct table access
         for any user regardless of role.

CREATE USER IF NOT EXISTS 'scav_login'@'%' IDENTIFIED BY '${DB_PASS_LOGIN}';
CREATE USER IF NOT EXISTS 'scav_admin'@'%' IDENTIFIED BY '${DB_PASS_ADMIN}';
CREATE USER IF NOT EXISTS 'scav_user'@'%' IDENTIFIED BY '${DB_PASS_USER}';
CREATE USER IF NOT EXISTS 'scav_social'@'%' IDENTIFIED BY '${DB_PASS_SOCIAL}';



-- ----------------------------------------------------------------------------
-- -                              USERS TABLE                                 -
-- ----------------------------------------------------------------------------

-- Users table stored procedures ('scav_login')
-- ----------------------------------------------------------------------------
GRANT EXECUTE ON PROCEDURE scavengers.sp_fetch_user_auth TO 'scav_login'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_create_user_request TO 'scav_login'@'%';



-- Users table administrative stored procedures ('scav_admin')
-- ----------------------------------------------------------------------------
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_fetch_users TO 'scav_admin'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_approve_user TO 'scav_admin'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_deny_user TO 'scav_admin'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_fetch_user TO 'scav_admin'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_suspend_user TO 'scav_admin'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_ban_user TO 'scav_admin'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_reinstate_user TO 'scav_admin'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_delete_user TO 'scav_admin'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_reset_password TO 'scav_admin'@'%';



-- ----------------------------------------------------------------------------
--                           ANNOUNCEMENTS TABLE                              -
-- ----------------------------------------------------------------------------

-- Announcements table stored procedures ('scav_social')
-- ----------------------------------------------------------------------------
GRANT EXECUTE ON PROCEDURE scavengers.sp_fetch_announcements TO 'scav_social'@'%';



-- Announcements table administrative stored procedures ('scav_admin')
-- ----------------------------------------------------------------------------
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_create_announcement TO 'scav_admin'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_update_announcement TO 'scav_admin'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_delete_announcement TO 'scav_admin'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_fetch_announcement TO 'scav_admin'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_fetch_announcements TO 'scav_admin'@'%';



-- ----------------------------------------------------------------------------
--                              REPORTS TABLE                                 -
-- ----------------------------------------------------------------------------

-- Reports table stored procedures ('scav_user')
-- ----------------------------------------------------------------------------
GRANT EXECUTE ON PROCEDURE scavengers.sp_create_report TO 'scav_user'@'%';


-- Reports table administrative stored procedures ('scav_admin')
-- ----------------------------------------------------------------------------
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_fetch_reports TO 'scav_admin'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_fetch_report TO 'scav_admin'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_update_report TO 'scav_admin'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_delete_report TO 'scav_admin'@'%';



-- ----------------------------------------------------------------------------
--                             REQUESTS TABLE                                 -
-- ----------------------------------------------------------------------------

-- Requests table stored procedures ('scav_user')
-- ----------------------------------------------------------------------------
GRANT EXECUTE ON PROCEDURE scavengers.sp_create_request TO 'scav_user'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_fetch_requests_by_user TO 'scav_user'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_fetch_requests_by_status TO 'scav_user'@'%';


-- Requests table stored administrative procedures ('scav_admin')
-- ----------------------------------------------------------------------------
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_fetch_requests TO 'scav_admin'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_fetch_request TO 'scav_admin'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_update_request TO 'scav_admin'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_delete_request TO 'scav_admin'@'%';



FLUSH PRIVILEGES;
EOF