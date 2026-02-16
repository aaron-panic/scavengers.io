# site/components/layout.py - site layout definitions
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



from typing import List, Optional
from .base import Component

class LayoutThreeColumn(Component):
    """
    The standard 3-column application layout.
    1. Sidebar: Navigation (Left)
    2. Content: Main View (Center)
    3. Visuals: Effects/Decorations (Right)
    """
    def __init__(
        self, 
        sidebar: List[Component], 
        content: List[Component],
        content_title: Optional[str] = None,
        visuals: Optional[List[Component]] = None,
        user=None, 
        **kwargs
    ):
        super().__init__(**kwargs)
        self.sidebar = sidebar
        self.content = content
        self.content_title = content_title
        self.visuals = visuals or []
        self.user = user

    @property
    def template(self) -> str:
        return 'layout_3col.html'