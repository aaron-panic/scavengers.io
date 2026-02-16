# site/components/page.py - base page container class
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



from typing import List, Dict, Optional
from .base import Component
from config import CSS_DEFAULT_SHEETS, JS_DEFAULT_SCRIPTS

class Page(Component):
    """
    The root node. Represents the <html> document.
    Manages global resources (CSS/JS) and the main Layout.
    """

    def __init__(
        self, 
        title: str, 
        layout: Component, 
        stylesheets: Optional[List[str]] = None,
        scripts: Optional[List[str]] = None,
        meta_tags: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.title = title
        self.layout = layout
        
        # Default global styles (always present)
        self.stylesheets = CSS_DEFAULT_SHEETS
        if stylesheets:
            self.stylesheets.extend(stylesheets)
            
        # Default global scripts
        self.scripts = JS_DEFAULT_SCRIPTS 
        if scripts:
            self.scripts.extend(scripts)

        # Meta tags (description, viewport, etc)
        self.meta_tags = meta_tags or []

    @property
    def template(self) -> str:
        return 'base_graph.html'