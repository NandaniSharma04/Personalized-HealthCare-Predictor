import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(r"c:\Users\G SAI SHARANYA\OneDrive\Desktop\Personalized-HealthCare-Predictor-main")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import create_app
from backend.models import User, PredictionHistory, HealthProfile, db

app = create_app()

with app.app_context():
    print("="*60)
    print("TESTING BACKEND DASHBOARD ENDPOINTS & DATABASE")
    print("="*60)
    
    users = User.query.all()
    print(f"Total Database Users: {len(users)}")
    for u in users[:5]:
        print(f" - User ID: {u.id}, Name: '{u.name}', Email: '{u.email}', Role: '{u.role}'")
        preds = PredictionHistory.query.filter_by(user_id=u.id).count()
        print(f"   -> Predictions Count: {preds}")
    
    client = app.test_client()
    if users:
        with client.session_transaction() as sess:
            sess['_user_id'] = str(users[0].id)
            sess['_fresh'] = True
    
    res = client.get('/api/user/dashboard')
    print(f"\nGET /api/user/dashboard Status Code: {res.status_code}")
    data = res.get_json()
    print("Response KPI Stats:", json.dumps(data.get('kpi_stats', {}), indent=2))
    print("Recent Prediction:", json.dumps(data.get('recent_prediction', {}), indent=2))
    print("Profile Completion:", data.get('profile_completion'))
