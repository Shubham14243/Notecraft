from app import create_app, db
from app.models import User, Folder, MarkdownFile

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Folder': Folder, 'MarkdownFile': MarkdownFile}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create default user for testing
        if not User.query.filter_by(email='test@example.com').first():
            user = User(email='test@example.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            print("Default user created: test@example.com / password")
    app.run(debug=True)
