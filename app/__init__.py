from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

def create_app(config_class=Config):
    app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')
    app.config.from_object(config_class)
    
    bcrypt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db, directory='app/migrations')

    from app.routes.auth import bp as auth_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    @app.errorhandler(404)
    def page_not_found(e):
        response = {
            "code": 404,
            "status": "failure",
            "message": "Route Not Exists!"
        }
        return jsonify(response), 404
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "okayyyy!"}), 200
    
    return app
