from flask import session, redirect, url_for, render_template

def check_access(allowed_roles):
    # Return to login if not logged in
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    # Render unauthorized if not allowed by role
    if session.get('role') not in allowed_roles:
        return render_template('unauthorized.html', title='unauthorized'), 403

    return None
