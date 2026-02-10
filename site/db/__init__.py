# db.__init__.py - For ease of importing
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

from .core import get_db, close_dbs, execute_query, execute_procedure
from .announcements import (
    fetch_announcements,
    create_announcement,
    update_announcement,
    delete_announcement,
    get_announcement,
    list_announcements_admin
)
from .users import (
    fetch_user_auth,
    fetch_all_users,
    approve_user,
    deny_user,
    fetch_user_details,
    suspend_user,
    ban_user,
    reinstate_user,
    delete_user,
    reset_password
)

from .reports import (
    create_report,
    fetch_reports,
    update_report,
    delete_report
)

from .requests import (
    fetch_requests_by_status,
    fetch_requests_by_uid,
    create_request,
    delete_request
)