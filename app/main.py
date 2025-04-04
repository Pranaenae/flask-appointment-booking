from logging import StringTemplateStyle 
import os 
import urllib 
from typing import Dict, Any, Optional, Tuple
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required, create_refresh_token
from flask_cors import CORS
from datetime import datetime, timedelta
from sqlalchemy import Integer, String, update, exists, select
from sqlalchemy.orm import joinedload
from .database import db, db_url
from .models import Users, Appointments
from flask_migrate import Migrate

app = Flask(__name__)
CORS(app, expose_headers=['Access-Token', 'Refresh-Token'])
app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY' , 'helloworld')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.environ['JWT_ACCESS_TOKEN_EXPIRES'])
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
migrate = Migrate(app, db)
db.init_app(app)
jwt = JWTManager(app)

@app.route("/")
@app.route("/ping")
def ping() -> Tuple [str, int]:
    return "App is running", 200

@app.route("/users")
@jwt_required
def user_list():
    users = Users.query.order_by(Users.username).all()
    users_data = [{"id": user.id, "username": user.username} for user in users]
    print(users)
    return {
        "users": users_data
    }, 400

@app.route('/refresh', methods=['GET'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    response = jsonify({"message": "Access token has been refreshed"})
    response.headers['Access-Token'] = new_access_token
    return response

@app.route('/login', methods=['POST'])
def login() -> Tuple[Dict[str, Any],int]:
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = db.get_or_404(Users, username)

    if password != user.password:
        return jsonify({"error": "Username or password do not match"}), 400

    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    response = jsonify({"user": username, "msg": "Logged In"})
    response.status_code = 200
    response.headers['Access-Token'] = access_token
    response.headers['Refresh-Token'] = refresh_token
    return response

@app.route("/protected", methods=["GET"])
@jwt_required()
def protected()-> Tuple[Dict[str, Any],int]:
    current_user= get_jwt_identity()
    return {
        "logged_in_as": current_user
    },200

@app.route("/appointments", methods=["GET"])
@jwt_required()
def get_appointments() -> Tuple[Dict[str, Any],int]:
    appointment_date=request.args.get("date")
    try:
        datetime.strptime(appointment_date, "%Y-%m-%d")
    except (ValueError, TypeError):
        return {"error": "Invalid date format. Use YYYY-MM-DD."}, 400
    try:
        return Appointments.get_appointments(appointment_date)
                
    except Exception as e:
        print(e)
        return {"error": "An internal error occurred."}, 500

@app.route("/appointments/add", methods=["GET"])
@jwt_required()
def add_appointment() -> Tuple[Dict[str, Any],int]:
    current_user= get_jwt_identity()
    user = db.get_or_404(Users, current_user)
    date=request.args.get("date")
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except (ValueError, TypeError):
        return {"error": "Invalid date format. Use YYYY-MM-DD."}, 400
    return user.book_appointment(date)

@app.route("/appointments/cancel", methods=["GET"])
@jwt_required()
def cancel_appointment() -> Tuple[Dict[str, Any],int]:
    current_user= get_jwt_identity()
    user = db.get_or_404(Users, current_user)
    date=request.args.get("date")
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except (ValueError, TypeError):
        return {"error": "Invalid date format. Use YYYY-MM-DD."}, 400
    return user.cancel_appointment(date)
