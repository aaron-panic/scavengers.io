from flask import Blueprint, render_template
from middleware import check_access

social_bp = Blueprint('social', __name__, url_prefix='/social')

@social_bp.before_request
def restrict_access():
    return check_access(['admin', 'user', 'social'])

@social_bp.route('/announce')
def announce():
    return render_template('announce.html', title='announce')

@social_bp.route('/post')
def post():
    return render_template('post.html', title='post')

@social_bp.route('/bulletin')
def bulletin():
    return render_template('bulletin.html', title='bulletin')

@social_bp.route('/chat')
def chat():
    return render_template('chat.html', title='chat')

@social_bp.route('/app')
def app():
    return render_template('app.html', title='app')
