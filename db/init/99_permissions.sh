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
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_list_users TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_approve_requested TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_deny_requested TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_get_user_details TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_suspend_user TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_ban_user TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_reinstate_user TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_delete_user TO 'scav_admin_bot'@'%';
GRANT EXECUTE ON PROCEDURE scavengers.sp_admin_reset_password TO 'scav_admin_bot'@'%';

-- Admin
CREATE USER IF NOT EXISTS 'scav_admin'@'%' IDENTIFIED BY '${DB_PASS_ADMIN}';
GRANT ALL PRIVILEGES ON scavengers.* TO 'scav_admin'@'%';

-- Social
CREATE USER IF NOT EXISTS 'scav_social'@'%' IDENTIFIED BY '${DB_PASS_SOCIAL}';

-- User
CREATE USER IF NOT EXISTS 'scav_user'@'%' IDENTIFIED BY '${DB_PASS_USER}';

FLUSH PRIVILEGES;
EOF
