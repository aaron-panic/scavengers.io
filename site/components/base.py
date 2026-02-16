# site/components/base.py - ui components base classes
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

from typing import Dict, Any, List, Optional

class Component:
    """
    The abstract base class for all UI elements (Layouts, Containers, Widgets).
    """

    def __init__(self, **kwargs):
        self.props: Dict[str, Any] = kwargs
        
    @property
    def template(self) -> str:
        raise NotImplementedError("Component must define a template.")

class Container(Component):
    """
    Base class for components that hold other components.
    """
    
    def __init__(self, children: Optional[List[Component]] = None, **kwargs):
        super().__init__(**kwargs)
        self.children = children or []

    def add_child(self, component: Component):
        self.children.append(component)