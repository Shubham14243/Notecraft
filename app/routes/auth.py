from flask import Blueprint, jsonify, request

bp = Blueprint('auth', __name__)

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    return """<html><body><h1>Auth Route</h1><p>This is a placeholder for the auth route.</p></body></html>"""