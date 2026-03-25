import logging
from datetime import datetime
from flask import Blueprint, request, render_template, flash, redirect, session, url_for

from app.utils import Validator
from app.models import User, Folder, MarkdownFile
from app import db
from app import bcrypt

bp = Blueprint('main', __name__)

logger = logging.getLogger(__name__)

@bp.route('/', methods=['GET'])
def index():
    
    if session.get("user"):
            return redirect(url_for("main.home"))
    
    return render_template('index.html')


@bp.route('/home', methods=['GET'])
def home():
    try:
        if not session.get("user"):
            return redirect(url_for("auth.login"))
    
        user = session.get("user")
        
        session["path"] = [{"id": user.get("root_folder_id"), "name": "Home"}]
        session["current_folder_id"] = 0
        
        fav = request.args.get("fav")
        
        folders = Folder.query.filter_by(parent_id=user.get("root_folder_id")).all()
        folders.sort(key=lambda f: f.created_at, reverse=True)
        
        if fav == "true":
            files = MarkdownFile.query.filter_by(folder_id=user.get("root_folder_id"),favorite=True).all()
        else:
            files = MarkdownFile.query.filter_by(folder_id=user.get("root_folder_id")).all()
        files.sort(key=lambda f: f.updated_at, reverse=True)
        
        return render_template('dashboard.html', flag="dashboard", path=session["path"], user=user, folders=folders, files=files)
    
    except Exception as e:
        logger.error(f"Unexpected error in home route: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        session.clear()
        return redirect(url_for('auth.login'))
    

@bp.route('/settings', methods=['GET', 'POST'])
def settings():
    try:
        if not session.get("user"):
            return redirect(url_for("auth.login"))
    
        user = session.get("user")
        
        if request.method == "POST":
            
            if request.form.get("type") == "update_username":
            
                username = request.form.get("username")
                
                username_error = Validator.validate_username(username)
                if username_error:
                    flash(username_error, 'error')
                    return redirect(url_for('main.settings'))
                
                existing_user = User.query.filter_by(username=username).first()
                if existing_user and existing_user.id != user.get("id"):
                    flash('Username already taken!', 'error')
                    return redirect(url_for('main.settings'))
                
                user_record = User.query.get(user.get("id"))
                user_record.username = username
                
                db.session.commit()
                
                user["username"] = username
                session["user"] = user
                flash('Username updated successfully!', 'success')
                
            elif request.form.get("type") == "update_password":
                
                current_password = request.form.get("current_password")
                new_password = request.form.get("new_password")
                confirm_password = request.form.get("confirm_password")
                
                if new_password != confirm_password:
                    flash('New password and confirm password do not match!', 'error')
                    return redirect(url_for('main.settings'))
                
                password_error = Validator.validate_password(new_password)
                if password_error:
                    flash(password_error, 'error')
                    return redirect(url_for('main.settings'))
                
                user_record = User.query.get(user.get("id"))
                
                if not bcrypt.check_password_hash(user_record.password_hash, current_password):
                    flash('Current password is incorrect!', 'error')
                    return redirect(url_for('main.settings'))
                
                user_record.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
                db.session.commit()
                
                flash('Password updated successfully!', 'success')
                
            elif request.form.get("type") == "delete_account":
                
                password = request.form.get("password_confirmation")
                
                user_record = User.query.get(user.get("id"))
                
                if not bcrypt.check_password_hash(user_record.password_hash, password):
                    flash('Password is incorrect! Account deletion cancelled.', 'error')
                    return redirect(url_for('main.settings'))
                
                db.session.delete(user_record)
                db.session.commit()
                
                flash('Account and all associated data deleted successfully!', 'success')
                session.clear()
                return redirect(url_for('auth.login'))
            
        
        return render_template('settings.html', user=user)
    
    except Exception as e:
        logger.error(f"Unexpected error in home route: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        session.clear()
        return redirect(url_for('main.home'))    
