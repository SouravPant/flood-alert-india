import os
from flask import Flask, jsonify, send_from_directory # type: ignore
from flask_cors import CORS # type: ignore

import models # type: ignore
from routes.locations import locations_bp # type: ignore
from routes.alerts import alerts_bp # type: ignore
from routes.incidents import incidents_bp # type: ignore
from routes.damage_reports import damage_reports_bp # type: ignore
from routes.search import search_bp # type: ignore
from routes.evacuation import evacuation_bp # type: ignore
from flask import request, abort # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore

# Pre-generate hash for "flood@0001" (Proper encryption method as requested)
ADMIN_PASSWORD_HASH = 'scrypt:32768:8:1$4DTwLi9BfKR8h91m$a480d4402d08bbcd163441b3bb6305d4232c6e7c2a8b41d1fe3d3275e3ad3f0174d8ec823b8ece0a97d1d336ef21af2305171dd36e97749dd1601312383664e2'

CLIENT_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'client', 'dist'))
app = Flask(__name__, static_folder=os.path.join(CLIENT_DIST, 'assets'), static_url_path='/assets')
CORS(app)

app.register_blueprint(locations_bp)
app.register_blueprint(alerts_bp)
app.register_blueprint(incidents_bp)
app.register_blueprint(damage_reports_bp)
app.register_blueprint(search_bp)
app.register_blueprint(evacuation_bp)

# Authentication Middleware for Admin Routes
@app.before_request
def require_admin_auth():
    # Only protect mutation routes (POST, PATCH, DELETE) and admin GET routes
    protected_paths = [
        ('/api/alerts', ['POST', 'PATCH', 'DELETE']),
        ('/api/incidents', ['POST', 'PATCH', 'DELETE']),
        ('/api/damage-reports', ['GET', 'PATCH', 'DELETE']) # Admin reviews damage reports
    ]
    
    for path, methods in protected_paths:
        if request.path.startswith(path) and request.method in methods:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                abort(401, description="Admin authentication required")
            
            token = auth_header.split(' ')[1]
            if not check_password_hash(ADMIN_PASSWORD_HASH, token):
                abort(401, description="Invalid admin password")

@app.route('/favicon.svg')
def favicon():
    return send_from_directory(CLIENT_DIST, 'favicon.svg')

@app.route('/icons.svg')
def icons():
    return send_from_directory(CLIENT_DIST, 'icons.svg')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(CLIENT_DIST, path)):
        return send_from_directory(CLIENT_DIST, path)
    return send_from_directory(CLIENT_DIST, 'index.html')

# Initialize DB
models.init_db()

if __name__ == '__main__':
    print("Serving on http://localhost:5000")
    app.run(debug=True, port=5000)
