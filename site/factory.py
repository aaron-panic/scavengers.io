# site/factory.py
# Copyright (C) 2026 Aaron Reichenbach

from typing import List
from flask import session, url_for, get_flashed_messages

from components.base import Component
from components.page import Page
from components.layout import LayoutThreeColumn
from components.widgets import WidgetNavigation
from components.widgets import WidgetFlashModal

def build_page(content: List[Component], title: str) -> Page:
    """
    Assembles the standard page structure with navigation and layout.
    """
    
    # navigation
    username = session.get('username', 'anon_user')
    role = session.get('role')

    links_logged_out = [
        {'label': 'login', 'href': url_for('auth.login')},
        {'label': 'register', 'href': url_for('auth.register')}
    ]

    links_admin = [
        {'label': 'admin', 'href': url_for('admin.dashboard')}
    ]

    links_user = [
        {'label': 'report', 'href': url_for('users.report')},
        {'label': 'request', 'href': url_for('users.requests')},
        {'label': 'media', 'href': url_for('users.media')},
        {'label': 'dev', 'href': url_for('users.dev')},
        {'label': 'board', 'href': url_for('users.board')}
    ]

    links_social = [
        {'label': 'announcements', 'href': url_for('social.announcements')},
        {'label': 'feed', 'href': url_for('social.feed')},
        {'label': 'chat', 'href': url_for('social.chat')},
        {'label': 'profile', 'href': url_for('social.profile')}
    ]

    links_all = [
        {'label': 'logout', 'href': url_for('auth.logout')}
    ]

    links = []

    if not role:
        links = links_logged_out
    else:
        if role == 'admin':
            links.extend(links_admin)
        if role in ['admin', 'user']:
            links.extend(links_user)
        if role in ['admin', 'user', 'social']:
            links.extend(links_social)
        links.extend(links_all)

    nav = WidgetNavigation(
        title=username,
        links=links
    )

    messages = get_flashed_messages(with_categories=True)
    flash_widget = WidgetFlashModal(messages=messages)
    content.append(flash_widget)

    layout = LayoutThreeColumn(
        sidebar=[nav],
        content=content,
        content_title=".scavengers.io",
        visuals=[]
    )

    page = Page(
        title=title,
        layout=layout
    )

    return page