# utils.py - Utility functions
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

import html
import re
import math
from flask import flash, url_for
from markupsafe import Markup

from config import PASSWORD_POLICY, PASSWORD_ALLOWED_SYMBOLS



# -----------------------------------------------------------------------------
# Authorization Security
# -----------------------------------------------------------------------------

def validate_password(password: str) -> bool:
    """
    Validate password against global policy provided in config.py

    :param password: plain text password to check
    :return: True if valid, False otherwise.
    """

    # Length Maximum Check.
    if len(password) > PASSWORD_POLICY['max-length']:
        return False
    
    # Length Minimum Check.
    if len(password) < PASSWORD_POLICY['min-length']:
        return False

    # Allow user to skip all other checks if password is long enough as entropy
    # will be high enough to be secure. As the password is already confirmed to
    # be < 'max-length' we only have to check it's at the 'safe-length' or more.
    if len(password) >= PASSWORD_POLICY['safe-length']:
        return True
    
    # Complexity Checks
    if PASSWORD_POLICY['require-lower'] and not re.search(r"[a-z]", password):
        return False
    if PASSWORD_POLICY['require-upper'] and not re.search(r"[A-Z]", password):
        return False
    if PASSWORD_POLICY['require-digit'] and not re.search(r"\d", password):
        return False
    if PASSWORD_POLICY['require-symbol']:
        # ensure symbols are escaped properly
        symbols = re.escape(PASSWORD_ALLOWED_SYMBOLS)
        if not re.search(f"[{symbols}]", password):
            return False
    
    return True
    
# -----------------------------------------------------------------------------

def format_post(text):
    if not text:
        return ""
    
    # Escape HTML (Security)
    text = html.escape(text)
    
    # Parse Links (State Machine)
    result = []
    i = 0
    n = len(text)
    
    while i < n:
        # Check for start of link
        if text[i] == '[':
            # Find the closing ']' for the label
            label_start = i + 1
            label_end = -1
            
            # Scan for ']' (We assume labels don't have nested brackets for simplicity, 
            # or we could count them too. For now, simple scan works for 99% of cases)
            for j in range(label_start, n):
                if text[j] == ']':
                    label_end = j
                    break
            
            # Check if ']' is followed immediately by '('
            if label_end != -1 and label_end + 1 < n and text[label_end + 1] == '(':
                url_start = label_end + 2
                url_end = -1
                paren_depth = 1
                
                # Scan for the closing ')' accounting for nesting
                for k in range(url_start, n):
                    if text[k] == '(':
                        paren_depth += 1
                    elif text[k] == ')':
                        paren_depth -= 1
                    
                    if paren_depth == 0:
                        url_end = k
                        break
                
                # If valid link found, construct HTML and skip forward
                if url_end != -1:
                    label = text[label_start:label_end]
                    url = text[url_start:url_end]
                    
                    result.append(f'<a href="{url}">{label}</a>')
                    i = url_end + 1
                    continue
        
        # Fallback: Just append the current character
        result.append(text[i])
        i += 1
            
    formatted_text = "".join(result)
    
    # Formatting: Convert newlines to <br> to preserve structure
    final_html = formatted_text.replace('\n', '<br>')
    
    return Markup(final_html)

    # -----------------------------------------------------------------------------

def get_pagination_metadata(page: int, per_page: int, total_count: int, endpoint: str, **kwargs) -> dict:
    """

    Generate standard pagination metadata for templates.
    
    :param page: Current page number.
    :param per_page: Items per page.
    :param total_count: Total number of items.
    :param endpoint: The flask route endpoint to generate links for.
    :param kwargs: Additional arguments to pass to url_for (e.g. tab_sel).
    :return: Dictionary containing pagination state and links.
    """
    
    # Calculate pages
    # NOTE - avoid division by zero, default to 1 page if empty
    total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1
    
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        'page': page,
        'has_next': has_next,
        'has_prev': has_prev,
        'next_href': url_for(endpoint, page=page + 1, **kwargs) if has_next else '#',
        'prev_href': url_for(endpoint, page=page - 1, **kwargs) if has_prev else '#',
        'pages': total_pages
    }

# -----------------------------------------------------------------------------

def flash_form_errors(form):
    """
    Iterate over a FlaskForm's errors and flash them to the user.
    """

    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error in {getattr(form, field).label.text}: {error}", 'error')