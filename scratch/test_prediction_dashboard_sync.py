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
    print("TESTING PREDICTION SAVING AND DASHBOARD REAL-TIME UPDATES")
    print("="*60)
    
    users = User.query.all()
    test_user = users[0]
    
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
        sess['_fresh'] = True
    
    print("1. Running prediction for ['fever', 'chills', 'sweating', 'headache']...")
    pred_res = client.post('/api/predict', json={'symptoms': ['fever', 'chills', 'sweating', 'headache']})
    print(f"POST /api/predict Status: {pred_res.status_code}")
    print("Prediction Output:", json.dumps(pred_res.get_json(), indent=2))
    
    print("\n2. Fetching updated dashboard statistics...")
    dash_res = client.get('/api/user/dashboard')
    dash_data = dash_res.get_json()
    print("Updated KPI Stats:", json.dumps(dash_data.get('kpi_stats', {}), indent=2))
    print("Updated Recent Prediction:", json.dumps(dash_data.get('recent_prediction', {}), indent=2))
    print("Total Predictions in DB for User:", PredictionHistory.query.filter_by(user_id=test_user.id).count())
