# site/components/containers.py - containers for data members
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



from typing import Optional, List, Any
from .base import Component, Container



class ContainerStack(Container):
    """
    Renders children vertically with a consistent gap.
    """

    def __init__(self, gap: str = 'medium', **kwargs):
        super().__init__(**kwargs)
        self.gap = gap # 'small', 'medium', 'large'

    @property
    def template(self) -> str:
        return 'container_stack.html'

# -----------------------------------------------------------------------------

class ContainerGrid(Container):
    """
    Renders children in a CSS Grid.
    """

    def __init__(self, cols: int = 3, gap: str = 'medium', **kwargs):
        super().__init__(**kwargs)
        self.cols = cols
        self.gap = gap

    @property
    def template(self) -> str:
        return 'container_grid.html'

# -----------------------------------------------------------------------------

class ContainerPanel(Container):
    """
    A visible container with a background, border, optional title, and footer.
    Used for grouping related widgets (e.g. "User Details", "Action Bar").
    """
    
    def __init__(
        self,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        author: Optional[str] = None,
        timestamp: Optional[str] = None,
        footnote: Optional[str] = None,
        footer: Optional[Component] = None,
        collapsible: bool = False,
        start_collapsed: bool = False,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.title = title
        self.subtitle = subtitle
        self.author = author
        self.timestamp = timestamp
        self.footnote = footnote
        self.footer = footer
        self.collapsible = collapsible
        self.start_collapsed = start_collapsed

    @property
    def template(self) -> str:
        return 'container_panel.html'