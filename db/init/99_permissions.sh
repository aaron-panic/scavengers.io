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

-- scav_login_bot
CREATE USER IF NOT EXISTS 'scav_login_bot'@'%' IDENTIFIED BY '${DB_PASS_LOGIN_BOT}';
GRANT EXECUTE ON PROCEDURE scavengers.sp_get_user_auth TO 'scav_login_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_register_user TO 'scav_login_bot'@'%';

-- scav_admin_bot
CREATE USER IF NOT EXISTS 'scav_admin_bot'@'%' IDENTIFIED BY '${DB_PASS_ADMIN_BOT}';

-- Admin (Users)
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_list_users TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_approve_requested TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_deny_requested TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_get_user_details TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_suspend_user TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_ban_user TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_reinstate_user TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_delete_user TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_reset_password TO 'scav_admin_bot'@'%';

-- Admin (Announcements)
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_create_announcement TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_update_announcement TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_delete_announcement TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_get_announcement TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_list_announcements TO 'scav_admin_bot'@'%';

-- Admin (Reports)
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_list_reports TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_update_report TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_delete_report TO 'scav_admin_bot'@'%';

-- Admin (Requests)
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_list_requests TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_get_request TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_update_request TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_delete_request TO 'scav_admin_bot'@'%';

-- Social
CREATE USER IF NOT EXISTS 'scav_social'@'%' IDENTIFIED BY '${DB_PASS_SOCIAL}';
GRANT EXECUTE ON PROCEDURE scavengers.sp_get_announcements TO 'scav_social'@'%';

-- User
CREATE USER IF NOT EXISTS 'scav_user'@'%' IDENTIFIED BY '${DB_PASS_USER}';
GRANT EXECUTE ON PROCEDURE scavengers.sp_get_requests_by_status TO 'scav_user'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_get_requests_by_uid TO 'scav_user'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_create_report TO 'scav_user'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_create_request TO 'scav_user'@'%';

FLUSH PRIVILEGES;
EOF