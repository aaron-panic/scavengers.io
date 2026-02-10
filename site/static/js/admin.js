// admin.js - Confirmation dialog generation
// Copyright (C) 2026 Aaron Reichenbach

// This program is free software: you can redistribute it and/or modify         
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.

// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

// Generic submission confirmation
document.addEventListener('submit', function(e) {
    // Check if the submitted form has the 'confirm-action' class
    if (e.target && e.target.classList.contains('confirm-action')) {
        const message = e.target.getAttribute('data-message') || 'Are you sure?';
        
        if (!confirm(message)) {
            e.preventDefault(); // Stop submission if user clicks Cancel
        }
    }
});