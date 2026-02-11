# db.__init__.py - For importing module
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

from .core import (
    get_db,
    close_dbs, 
    execute_procedure
)

from .announcements import (
    fetch_announcements,
    admin_create_announcement,
    admin_update_announcement,
    admin_delete_announcement,
    admin_fetch_announcement,
    admin_fetch_announcements
)

from .reports import (
    create_report,
    admin_fetch_reports,
    admin_fetch_report,
    admin_update_report,
    admin_delete_report
)

from .requests import (
    fetch_requests_by_status,
    fetch_requests_by_user,
    create_request,
    admin_fetch_requests,
    admin_fetch_request,
    admin_update_request,
    admin_delete_request
)

from .users import (
    fetch_user_auth,
    admin_fetch_users,
    admin_approve_user,
    admin_deny_user,
    admin_fetch_user,
    admin_suspend_user,
    admin_ban_user,
    admin_reinstate_user,
    admin_delete_user,
    admin_reset_password
)