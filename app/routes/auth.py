from datetime import datetime
from flask import Blueprint, request, render_template, flash, redirect, session, url_for
from app.utils import Validator
from app.models import User, Folder
from app import db
from app import bcrypt
import logging

bp = Blueprint('auth', __name__)

# Set up logging
logger = logging.getLogger(__name__)

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        if session.get("user"):
            return redirect(url_for("main.home"))
        
        if request.method == 'POST':
            username = request.form['username'].strip()
            email = request.form['email'].strip().lower()
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            
            # Basic validation
            if not username:
                flash('Username is required!', 'error')
                return redirect(url_for('auth.signup'))
            
            if not email:
                flash('Email is required!', 'error')
                return redirect(url_for('auth.signup'))
            
            if not password or not confirm_password:
                flash('Password is required!', 'error')
                return redirect(url_for('auth.signup'))
            
            # Validate inputs
            username_error = Validator.validate_username(username)
            if username_error:
                flash(username_error, 'error')
                return redirect(url_for('auth.signup'))
            
            email_error = Validator.validate_email(email)
            if email_error:
                flash(email_error, 'error')
                return redirect(url_for('auth.signup'))
            
            password_error = Validator.validate_password(password)
            if password_error:
                flash(password_error, 'error')
                return redirect(url_for('auth.signup'))

            if password != confirm_password:
                flash('Passwords do not match!', 'error')
                return redirect(url_for('auth.signup'))
            
            # Check for existing user within a transaction
            try:
                existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
                if existing_user:
                    flash('Username or Email already taken!', 'error')
                    return redirect(url_for('auth.signup'))
                
                # Hash password
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

                # Create new user
                new_user = User(
                    username=username,
                    email=email,
                    password_hash=hashed_password,
                    created_at=datetime.now()
                )

                db.session.add(new_user)
                db.session.flush()  # Get the user ID without committing

                # Create root folder
                folder = Folder(
                    name=f'root_{username}',
                    user_id=new_user.id,
                    created_at=datetime.now()
                )

                db.session.add(folder)
                db.session.flush()  # Get the folder ID without committing

                # Update user with root folder ID
                new_user.root_folder_id = folder.id
                db.session.commit()

                flash('User signed up successfully!', 'success')
                return redirect(url_for('auth.login'))
            
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error during user registration: {str(e)}")
                flash('An error occurred during registration. Please try again.', 'error')
                return redirect(url_for('auth.signup'))
        
        return render_template('auth/signup.html')
    
    except Exception as e:
        logger.error(f"Unexpected error in signup route: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('auth.signup'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if session.get("user"):
            return redirect(url_for("main.home"))
        
        if request.method == 'POST':
            email = request.form['email'].strip().lower()
            password = request.form['password']
            
            if not email or not password:
                flash('Email and Password are required!', 'error')
                return redirect(url_for('auth.login'))
            
            # Validate inputs
            email_error = Validator.validate_email(email)
            if email_error:
                flash(email_error, 'error')
                return redirect(url_for('auth.login'))

            user = User.query.filter_by(email=email).first()

            if user and bcrypt.check_password_hash(user.password_hash, password):
                # Store user info in session
                session["user"] = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "root_folder_id": user.root_folder_id
                }
                
                session["path"] = ["Home"]
                
                flash(f'Hi {user.username}!', 'success')
                return redirect(url_for('main.home'))
            else:
                flash('Invalid email or password!', 'error')

        return render_template('auth/login.html')
    
    except Exception as e:
        logger.error(f"Unexpected error in login route: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('auth.login'))


@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    try:
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        
        session.clear()  # More secure than deleting individual keys
        
        flash("Logged Out Successfully!", "success")
        return redirect(url_for("auth.login"))
    
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        # Even if there's an error, we should redirect to login
        session.clear()
        return redirect(url_for("auth.login"))