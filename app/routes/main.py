from datetime import datetime
from flask import Blueprint, request, render_template, flash, redirect, session, url_for
from app.utils import Validator
from app.models import User, Folder, MarkdownFile
from app import db
from app import bcrypt
import logging

bp = Blueprint('main', __name__)

# Set up logging
logger = logging.getLogger(__name__)

@bp.route('/', methods=['GET'])
@bp.route('/home', methods=['GET'])
def home():
    try:
        if not session.get("user"):
            return redirect(url_for("auth.login"))
    
        user = session.get("user")
        
        session["path"] = [{"id": user.get("root_folder_id"), "name": "Home"}]
        session["current_folder_id"] = 0
        
        folders = Folder.query.filter_by(parent_id=user.get("root_folder_id")).all()
        folders.sort(key=lambda f: f.created_at, reverse=True)
        
        files = MarkdownFile.query.filter_by(folder_id=user.get("root_folder_id")).all()
        files.sort(key=lambda f: f.updated_at, reverse=True)
        
        return render_template('dashboard.html', flag="dashboard", path=session["path"], user=user, folders=folders, files=files)
    
    except Exception as e:
        logger.error(f"Unexpected error in home route: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        session.clear()
        return redirect(url_for('auth.login'))