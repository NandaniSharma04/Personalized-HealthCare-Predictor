"""
HealthAI - Flask Application Factory & Server Main Entrypoint
"""
import os
import re
import sys
from pathlib import Path

# Ensure project root is in sys.path when running app.py directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, jsonify
from flask_cors import CORS
from flask_login import LoginManager

from backend.utils.db import db
from backend.models import User

# Import Blueprints
from backend.routes.auth_routes import auth_bp
from backend.routes.users_routes import users_bp
from backend.routes.health_routes import health_bp
from backend.routes.predict_routes import predict_bp
from backend.routes.recommend_routes import recommend_bp
from backend.routes.analytics_routes import analytics_bp
from backend.routes.admin_routes import admin_bp

def create_app(test_config=None):
    app = Flask(__name__)
    
    # Secret Key
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "healthai-flask-secret-key-2026")
    
    # Database URI (SQLite fallback or PostgreSQL from env, fixing postgres:// scheme for SQLAlchemy)
    raw_db_url = os.environ.get("DATABASE_URL")
    if raw_db_url and raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
        
    db_path = Path(__file__).resolve().parent / "healthai.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = raw_db_url or f"sqlite:///{db_path.as_posix()}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Required for Cross-Origin Authentication
    is_production = os.environ.get("RENDER") or (raw_db_url and "render.com" in raw_db_url)
    if is_production:
        app.config["SESSION_COOKIE_SAMESITE"] = "None"
        app.config["SESSION_COOKIE_SECURE"] = True
    else:
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
        app.config["SESSION_COOKIE_SECURE"] = False

    if test_config:
        app.config.update(test_config)

    # Initialize extensions
    db.init_app(app)

    # CORS Configuration
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        re.compile(r"https://.*\.vercel\.app"),
        re.compile(r"https://.*\.onrender\.com")
    ]
    frontend_env = os.environ.get("FRONTEND_URL")
    if frontend_env:
        for url in frontend_env.split(","):
            cleaned = url.strip()
            if cleaned and cleaned not in allowed_origins:
                allowed_origins.append(cleaned)

    CORS(
        app,
        supports_credentials=True,
        origins=allowed_origins,
        allow_headers=["*"],
        methods=["*"]
    )

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except Exception:
            return None

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({"success": False, "error": "Authentication required"}), 401

    # Root & Health check endpoints
    @app.route("/", methods=["GET"])
    @app.route("/health", methods=["GET"])
    def root_health():
        return jsonify({"status": "healthy", "success": True, "server": "HealthAI Flask API"}), 200

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(recommend_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        try:
            db.create_all()
        except Exception as err:
            print(f"[DB INIT WARNING] Could not pre-create tables: {err}", flush=True)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)