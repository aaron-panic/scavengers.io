from flask import Blueprint, render_template
from middleware import check_access
import db
from utils import format_post

social_bp = Blueprint('social', __name__, url_prefix='/social')

@social_bp.app_template_filter('format_post')
def format_post_filter(text):
    return format_post(text)

@social_bp.before_request
def restrict_access():
    return check_access(['admin', 'user', 'social'])

@social_bp.route('/announce')
def announce():
    posts = db.fetch_announcements()
    return render_template('announce.html', title='announce', posts=posts)

@social_bp.route('/feed')
def feed():
    return render_template('feed.html', title='feed')

@social_bp.route('/board')
def board():
    return render_template('board.html', title='board')

@social_bp.route('/chat')
def chat():
    return render_template('chat.html', title='chat')

@social_bp.route('/profile')
def profile():
    return render_template('profile.html', title='profile')
