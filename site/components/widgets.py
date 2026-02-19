# site/components/widgets.py - widgets for content rendering
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

from typing import List, Dict, Tuple, Any, Optional
from .base import Component

class WidgetStatCard(Component):
    """
    Displays a key metric (e.g., "Total Users: 150").
    """
    def __init__(
        self,
        label: str,
        value: Any,
        icon: str = '',
        trend: str = '',
        **kwargs
    ):
        super().__init__(**kwargs)
        self.label = label
        self.value = value
        self.icon = icon
        self.trend = trend

    @property
    def template(self) -> str:
        return 'widget_stat_card.html'

class WidgetTable(Component):
    """
    A data table with named columns and row actions.
    """
    def __init__(self,
    columns: List[Dict[str, str]],
    rows: List[Dict[str, Any]],
    **kwargs
    ):
        super().__init__(**kwargs)
        self.columns = columns # [{'key': 'id', 'label': 'ID'}, ...]
        self.rows = rows       # [{'id': 1, 'username': 'admin', 'actions': [...]}, ...]

    @property
    def template(self) -> str:
        return 'widget_table.html'

class WidgetForm(Component):
    """
    Renders a WTForm instance.
    """
    def __init__(
        self,
        form,
        buttons: List[Component],
        action: str = '',
        method: str = 'POST',
        form_id: str = '',
        render_actions: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.form = form
        self.buttons = buttons
        self.action = action
        self.method = method
        self.form_id = form_id
        self.render_actions = render_actions

    @property
    def template(self) -> str:
        return 'widget_form.html'
    
class WidgetButton(Component):
    """
    A standalone button.
    """
    def __init__(
        self,
        label: str,
        href: Optional[str] = None,
        button_type: str = 'button',
        style: str = 'primary',
        attrs: str = '',
        **kwargs
    ):
        super().__init__(**kwargs)
        self.label = label
        self.href = href
        self.button_type = button_type
        self.style = style
        self.attrs = attrs

    @property
    def template(self) -> str:
        return 'widget_button.html'

class WidgetNavigation(Component):
    """
    A vertical navigation sidebar with a header and list of links.
    """
    def __init__(
        self,
        title: str,
        links: List[Dict[str, str]],
        **kwargs
    ):
        super().__init__(**kwargs)
        self.title = title
        self.links = links 

    @property
    def template(self) -> str:
        return 'widget_navigation.html'

class WidgetFlashModal(Component):
    """
    A hidden modal that pops up if there are flash messages.
    """
    def __init__(self, messages: List[Tuple[str, str]], **kwargs):
        super().__init__(**kwargs)
        self.messages = messages

    @property
    def template(self) -> str:
        return 'widget_flash_modal.html'

class WidgetText(Component):
    """
    Renders a text block.
    """
    def __init__(self, content: str, style: str = 'body', **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.style = style

    @property
    def template(self) -> str:
        return 'widget_text.html'