# app.py - Main app configuration/launch
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

import os
from datetime import timedelta

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

from db import close_dbs
from extensions import limiter

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ['FLASK_SECRET_KEY'],
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=60),
        SESSION_COOKIE_SECURE=os.environ.get('FLASK_ENV') == 'production',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax'
    )

    # Trust X-forwarded-for headers (so limiter targets the right IP address) 
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    # Database Teardown
    app.teardown_appcontext(close_dbs)

    # Jinja2 loves whitespace... So let's try to not.
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    # Security stuff
    csrf.init_app(app)

    limiter.init_app(app)
    limiter._default_limits = ["100 per day", "20 per hour"]

    @app.after_request
    def add_security_headers(response):
        # Content Security Policy (CSP)
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none';"
        )

        # X-Content-Type-Options
        response.headers['X-Content-Type-Options'] = 'nosniff'

        return response

    # Blueprint Registration

    # Auth
    from blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    # Admin
    from blueprints.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    # User
    from blueprints.users import bp as users_bp
    app.register_blueprint(users_bp)

    # Social
    from blueprints.social import bp as social_bp
    app.register_blueprint(social_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)