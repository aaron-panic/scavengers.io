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
from markupsafe import Markup

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