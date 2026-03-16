from datetime import datetime
from flask import Blueprint, request, render_template, flash, redirect, session, url_for
from app.utils import Validator
from app.models import User, Folder, MarkdownFile
from app import db
from app import bcrypt
from app import utils
import logging

bp = Blueprint('file', __name__)

# Set up logging
logger = logging.getLogger(__name__)

# @bp.route('/view/<int:folder_id>', methods=['GET'])
# def view_folder(folder_id):
#     try:
#         if not session.get("user"):
#             return redirect(url_for("auth.login"))
    
#         user = session.get("user")
        
#         folders = Folder.query.filter_by(user_id=user.get("id"), parent_id=folder_id).all()
#         folders.sort(key=lambda f: f.created_at, reverse=True)
        
#         return render_template('dashboard.html', flag="folder", user=user, folders=folders)
    
#     except Exception as e:
#         logger.error(f"Unexpected error in view folder route: {str(e)}")
#         flash('An unexpected error occurred. Please try again.', 'error')
#         session.clear()
#         return redirect(url_for('auth.login'))


@bp.route('/editor/<int:file_id>', methods=['GET'])
def edit_file(file_id):
    try:
        if not session.get("user"):
            return redirect(url_for("auth.login"))
    
        user = session.get("user")
        
        file = MarkdownFile.query.get(file_id)
        if not file:
            flash('File not found!', 'error')
        
            if session.get('current_folder_id') and session.get('current_folder_id') != 0:
                return redirect(url_for('folder.view_folder', folder_id=session.get('current_folder_id')))
            return redirect(url_for('main.home'))
        
        return render_template('editor.html', user=user, file=file)
    
    except Exception as e:
        logger.error(f"Unexpected error in edit file route: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('main.home'))
    
    
@bp.route('/save/<int:file_id>', methods=['POST'])
def save_file(file_id):
    try:
        if not session.get("user"):
            return redirect(url_for("auth.login"))
    
        user = session.get("user")
        
        type = request.form.get('type')
        
        file = MarkdownFile.query.get(file_id)
        if not file:
            flash('File not found!', 'error')
        
            if session.get('current_folder_id') and session.get('current_folder_id') != 0:
                return redirect(url_for('folder.view_folder', folder_id=session.get('current_folder_id')))
            return redirect(url_for('main.home'))
        
        if type == 'continue':
            content = request.form.get('content')
            file.content = content
            db.session.commit()
            flash('File saved successfully!', 'success')
        elif type == 'exit':
            content = request.form.get('content')
            file.content = content
            db.session.commit()
            flash('File saved successfully!', 'success')
            if session.get('current_folder_id') and session.get('current_folder_id') != 0:
                return redirect(url_for('folder.view_folder', folder_id=session.get('current_folder_id')))
            return redirect(url_for('main.home'))
        
        return redirect(url_for('file.edit_file', file_id=file.id))
    
    except Exception as e:
        logger.error(f"Unexpected error in edit file route: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('main.home'))


@bp.route('/create', methods=['POST'])
def create_file():
    
    try:
    
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        
        name = request.form['file_name']
        folder_id = request.form.get('folder_id')
        user = session.get("user")
        user_id = user.get("id")
        
        name_error = Validator.validate_name(name)
        if name_error:
            flash(name_error, 'error')
            return redirect(url_for('main.home'))
        
        new_file = MarkdownFile(
            title=name,
            folder_id=folder_id,
            public_key=utils.Generator.generate_public_key(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.session.add(new_file)
        db.session.commit()
        
        flash('File created successfully!', 'success')
        
        if session.get('current_folder_id') and session.get('current_folder_id') != 0:
            return redirect(url_for('folder.view_folder', folder_id=session.get('current_folder_id')))

        return redirect(url_for('main.home'))
    
    except Exception as e:
        logger.error(f"Unexpected error in file route: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('main.home'))
    
@bp.route('/rename', methods=['POST'])
def rename_file():
    
    try:
    
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        
        name = request.form['file_name']
        file_id = request.form['file_id']
        
        name_error = Validator.validate_name(name)
        if name_error:
            flash(name_error, 'error')
            return redirect(url_for('main.home'))
        
        file = MarkdownFile.query.get(file_id)
        if not file:
            flash('File not found!', 'error')
            return redirect(url_for('main.home'))
        file.title = name
        db.session.commit()
        
        flash('File renamed successfully!', 'success')
        
        if session.get('current_folder_id') and session.get('current_folder_id') != 0:
            return redirect(url_for('folder.view_folder', folder_id=session.get('current_folder_id')))

        return redirect(url_for('main.home'))
    
    except Exception as e:
        logger.error(f"Unexpected error in home route: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        session.clear()
        return redirect(url_for('auth.login'))
    
    
@bp.route('/delete', methods=['POST'])
def delete_file():
    
    try:
    
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        
        file_id = request.form['file_id']
        
        
        file = MarkdownFile.query.get(file_id)
        if not file:
            flash('File not found!', 'error')
            return redirect(url_for('main.home'))
        db.session.delete(file)
        db.session.commit()
        
        flash('File deleted successfully!', 'success')
        
        if session.get('current_folder_id') and session.get('current_folder_id') != 0:
            return redirect(url_for('folder.view_folder', folder_id=session.get('current_folder_id')))

        return redirect(url_for('main.home'))
    
    except Exception as e:
        logger.error(f"Unexpected error in home route: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        session.clear()
        return redirect(url_for('auth.login'))