import logging
from datetime import datetime
from flask import Blueprint, request, render_template, flash, redirect, session, url_for

from app.utils import Validator
from app.models import User, Folder, MarkdownFile
from app import db
from app import utils

bp = Blueprint('file', __name__)

logger = logging.getLogger(__name__)

@bp.route('/view/<file_key>', methods=['GET'])
def view_file(file_key):
    try:
        
        status = 1
        
        file_data = MarkdownFile.query.filter_by(public_key=file_key).first()
        if not file_data:
            status = 0
            return render_template('preview.html', file=None, status=status)
            
        if not session.get("user") and file_data.sharing == False:
            status = -1
            return render_template('preview.html', file=None, status=status)
        
        return render_template('preview.html', file=file_data, status=status)
    
    except Exception as e:
        logger.error(f"Unexpected error in edit file route: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('main.home'))


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
        
        name_error = Validator.validate_name(name)
        if name_error:
            flash(name_error, 'error')
            return redirect(url_for('main.home'))
        
        new_file = MarkdownFile(
            title=name,
            folder_id=folder_id,
            public_key=utils.Generator.generate_public_key(),
            author=user.get("username"),
            favorite=False,
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
    
@bp.route('/mark', methods=['POST'])
def mark_file():
    
    try:
    
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        
        file_id = request.form['file_id']
        
        file = MarkdownFile.query.get(file_id)
        if not file:
            flash('File not found!', 'error')
            return redirect(url_for('main.home'))
        
        file.favorite = True if not file.favorite else False
        db.session.commit()
        
        flash('File marked successfully!', 'success')
        
        if session.get('current_folder_id') and session.get('current_folder_id') != 0:
            return redirect(url_for('folder.view_folder', folder_id=session.get('current_folder_id')))

        return redirect(url_for('main.home'))
    
    except Exception as e:
        logger.error(f"Unexpected error in home route: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        session.clear()
        return redirect(url_for('main.home'))
    
    
@bp.route('/share', methods=['POST'])
def file_sharing():
    
    try:
    
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        
        file_id = request.form['file_id']
        
        file = MarkdownFile.query.get(file_id)
        if not file:
            flash('File not found!', 'error')
            return redirect(url_for('main.home'))
        
        file.sharing = True if not file.sharing else False
        db.session.commit()
        
        flash('File sharing updated successfully!', 'success')
        
        if session.get('current_folder_id') and session.get('current_folder_id') != 0:
            return redirect(url_for('folder.view_folder', folder_id=session.get('current_folder_id')))

        return redirect(url_for('main.home'))
    
    except Exception as e:
        logger.error(f"Unexpected error in home route: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        session.clear()
        return redirect(url_for('main.home'))
    
    
@bp.route('/refresh', methods=['POST'])
def refresh_url():
    
    try:
    
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        
        file_id = request.form['file_id']
        
        file = MarkdownFile.query.get(file_id)
        if not file:
            flash('File not found!', 'error')
            return redirect(url_for('main.home'))
        
        file.public_key = utils.Generator.generate_public_key()
        db.session.commit()
        
        flash('URL refreshed successfully!', 'success')
        
        if session.get('current_folder_id') and session.get('current_folder_id') != 0:
            return redirect(url_for('folder.view_folder', folder_id=session.get('current_folder_id')))

        return redirect(url_for('main.home'))
    
    except Exception as e:
        logger.error(f"Unexpected error in home route: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        session.clear()
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
        return redirect(url_for('main.home'))
    
    
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
        return redirect(url_for('main.home'))