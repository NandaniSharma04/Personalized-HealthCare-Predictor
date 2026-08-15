"""Backend Flask package"""
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from backend.routes.auth_routes import auth_bp
from backend.routes.health_routes import health_bp
from backend.routes.predict_routes import predict_bp
from backend.routes.recommend_routes import recommend_bp
from backend.routes.analytics_routes import analytics_bp
from backend.routes.admin_routes import admin_bp
from backend.models import db, User

def create_app():
    import importlib.util
    spec = importlib.util.spec_from_file_location("backend_app_module", root / "backend" / "app.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.create_app()

app = create_app()
__all__ = ["app", "create_app", "auth_bp", "health_bp", "predict_bp", "recommend_bp", "analytics_bp", "admin_bp", "db", "User"]
