from datetime import datetime
from flask import Blueprint, request, render_template, flash, redirect, session, url_for
from app.utils import Validator
from app.models import User, Folder, MarkdownFile
from app import db
from app import bcrypt
import logging

bp = Blueprint('folder', __name__)

# Set up logging
logger = logging.getLogger(__name__)

@bp.route('/view/<int:folder_id>', methods=['GET'])
def view_folder(folder_id):
    try:
        if not session.get("user"):
            return redirect(url_for("auth.login"))
    
        user = session.get("user")
        
        folder = Folder.query.get(folder_id)
        if not folder:
            flash('Folder not found!', 'error')
            return redirect(url_for('main.home'))
        
        session["path"] = session.get("path", [{"id": user.get("root_folder_id"), "name": "Home"}])
        if any(f.get("id") == folder_id for f in session["path"]):
            # If folder is already in path, trim the path to that folder
            session["path"] = session["path"][:next(i for i, f in enumerate(session["path"]) if f.get("id") == folder_id) + 1]
        else:
            session["path"] = session.get("path", [{"id": user.get("root_folder_id"), "name": "Home"}]) + [{"id": folder_id, "name": folder.name}]
        session["current_folder_id"] = folder_id
        
        folders = Folder.query.filter_by(user_id=user.get("id"), parent_id=folder_id).all()
        folders.sort(key=lambda f: f.created_at, reverse=True)
        
        files = MarkdownFile.query.filter_by(folder_id=folder_id).all()
        files.sort(key=lambda f: f.updated_at, reverse=True)
        
        return render_template('dashboard.html', flag="folder", user=user, folders=folders, files=files)
    
    except Exception as e:
        logger.error(f"Unexpected error in folder view route: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('main.home'))
    

@bp.route('/create', methods=['POST'])
def create_folder():
    
    try:
    
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        
        name = request.form['folder_name']
        parent_id = request.form.get('parent_id')
        user = session.get("user")
        user_id = user.get("id")
        
        name_error = Validator.validate_name(name)
        if name_error:
            flash(name_error, 'error')
            return redirect(url_for('main.home'))
        
        new_folder = Folder(
            name=name,
            user_id=user_id,
            parent_id=parent_id if parent_id else None,
            created_at=datetime.now()
        )
        db.session.add(new_folder)
        db.session.commit()
        
        flash('Folder created successfully!', 'success')
        
        if session.get('current_folder_id') and session.get('current_folder_id') != 0:
            return redirect(url_for('folder.view_folder', folder_id=session.get('current_folder_id')))

        return redirect(url_for('main.home'))
    
    except Exception as e:
        logger.error(f"Unexpected error in folder create route: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('auth.login'))
    
@bp.route('/update', methods=['POST'])
def update_folder():
    
    try:
    
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        
        name = request.form['folder_name']
        folder_id = request.form['folder_id']
        
        name_error = Validator.validate_name(name)
        if name_error:
            flash(name_error, 'error')
            return redirect(url_for('main.home'))
        
        folder = Folder.query.get(folder_id)
        if not folder:
            flash('Folder not found!', 'error')
            return redirect(url_for('main.home'))
        folder.name = name
        db.session.commit()
        
        flash('Folder renamed successfully!', 'success')
        
        if session.get('current_folder_id') and session.get('current_folder_id') != 0:
            return redirect(url_for('folder.view_folder', folder_id=session.get('current_folder_id')))

        return redirect(url_for('main.home'))
    
    except Exception as e:
        logger.error(f"Unexpected error in folder update route: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('auth.login'))
    
    
@bp.route('/delete', methods=['POST'])
def delete_folder():
    
    try:
    
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        
        folder_id = request.form['folder_id']
        
        
        folder = Folder.query.get(folder_id)
        if not folder:
            flash('Folder not found!', 'error')
            return redirect(url_for('main.home'))
        db.session.delete(folder)
        db.session.commit()
        
        flash('Folder deleted successfully!', 'success')
        
        if session.get('current_folder_id') and session.get('current_folder_id') != 0:
            return redirect(url_for('folder.view_folder', folder_id=session.get('current_folder_id')))

        return redirect(url_for('main.home'))
    
    except Exception as e:
        logger.error(f"Unexpected error in folder delete route: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('main.home'))