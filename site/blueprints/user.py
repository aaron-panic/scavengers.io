from flask import Blueprint, render_template
from middleware import check_access

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.before_request
def restrict_access():
    return check_access(['admin','user'])

@user_bp.route('/media')
def media():
    return render_template('media.html', title='media')

@user_bp.route('/req')
def req():
    return render_template('req.html', title='req')

@user_bp.route('/report')
def report():
    return render_template('report.html', title='report')

@user_bp.route('/dev')
def dev():
    return render_template('dev.html', title='dev')
