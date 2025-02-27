from logging import StringTemplateStyle 
import os 
import urllib 
from typing import Dict, Any, Optional, Tuple
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required, create_refresh_token
import psycopg2
from psycopg2 import OperationalError, Error
from flask_cors import CORS
from datetime import datetime, timedelta
from sqlalchemy import Integer, String, update, exists, select
from database import db, db_url
from models import Users, Appointments

app = Flask(__name__)
CORS(app, expose_headers=['Access-Token', 'Refresh-Token'])
app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY' , 'helloworld')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.environ['JWT_ACCESS_TOKEN_EXPIRES'])
app.config["SQLALCHEMY_DATABASE_URI"] = db_url

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
    date=request.args.get("date")
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except (ValueError, TypeError):
        return {"error": "Invalid date format. Use YYYY-MM-DD."}, 400
    try:
        appointment = db.get_or_404(Appointments, date)
                
        return {
            "date": appointment.date,
            "totalAppointments": appointment.total_appointments,
            "bookedAppointments": appointment.booked_appointments
        }, 200
    except Exception as e:
        print(e)
        return {"error": "An internal error occurred."}, 500

@app.route("/appointments/add", methods=["GET"])
@jwt_required()
def add_appointment() -> Tuple[Dict[str, Any],int]:
    date=request.args.get("date")
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except (ValueError, TypeError):
        return {"error": "Invalid date format. Use YYYY-MM-DD."}, 400
    try:
        appointment = db.one_or_404(db.select(Appointments).filter_by(date=date))
        print("Result exists")
        if appointment.booked_appointments < appointment.total_appointments:
            result = db.session.execute(
                update(Appointments)
                .where(Appointments.date == date)
                .values(booked_appointments=Appointments.booked_appointments + 1)
            )

            print(f"Result: {result}")
            db.session.commit()
            print(f"Appointment booked for {date}")
            updated_appointment = db.session.execute(db.select(Appointments).filter_by(date=date)).scalar_one()
            print(f"Updated  appointment {updated_appointment}")
            return {
                "msg": f"Added appointment for date {date}",
                "totalAppointments": updated_appointment.total_appointments,
                "bookedAppointments": updated_appointment.booked_appointments
            }, 200
        else:
            print(f"Date {date} not found")
            return {"msg": f"Adding appointment for date {date} not allowed"}, 200

    except Exception as e:
        print(f"Error: {e}")
        return {"error": "An internal error occurred."}, 500


with app.app_context():
    db.create_all()
