from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    reset_token = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    root_folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'))
    
class Folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete="CASCADE"),
        nullable=False
    )

    parent_id = db.Column(
        db.Integer,
        db.ForeignKey('folder.id', ondelete="CASCADE"),
        nullable=True
    )

    created_at = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship(
        'User',
        backref=db.backref('folders', lazy=True, cascade="all, delete"),
        foreign_keys=[user_id]
    )

    parent = db.relationship(
        'Folder',
        remote_side=[id],
        backref=db.backref('children', cascade="all, delete")
    )

    files = db.relationship(
        'MarkdownFile',
        backref='folder',
        lazy=True,
        cascade='all, delete-orphan'
    )
    
class MarkdownFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, default='')
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=False)
    public_key = db.Column(db.String(255), nullable=False, unique=True)
    author = db.Column(db.String(80), nullable=True)
    favorite = db.Column(db.Boolean, default=False)
    sharing = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id', ondelete="CASCADE"), nullable=False)