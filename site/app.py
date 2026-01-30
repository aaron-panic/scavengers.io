import os
from datetime import timedelta

from flask import Flask
from flask_wtf.csrf import CSRFProtect

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

    # Database Teardown
    app.teardown_appcontext(close_dbs)

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

    # Home
    from blueprints.home import home_bp
    app.register_blueprint(home_bp)

    # Admin
    from blueprints.admin import admin_bp
    app.register_blueprint(admin_bp)

    # User
    from blueprints.user import user_bp
    app.register_blueprint(user_bp)

    # Social
    from blueprints.social import social_bp
    app.register_blueprint(social_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
