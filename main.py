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
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.engine import URL
from sqlalchemy import Integer, String

def get_db_connection():
    try: 
        required_env_vars = ['DB_HOST', 'DB_NAME', 'DB_USERNAME', 'DB_PASSWORD', 'DB_PORT']        
        for var in required_env_vars:
            if var not in os.environ:
                raise ValueError(f"Missing environment variable: {var}")
        connection = psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD'],
        port=os.environ['DB_PORT']
        )

        connection.autocommit = False

        return connection    

    except OperationalError as e:
        print(f"Error connecting to the database: {e}")
        raise
    
    except ValueError as e:
        print(f"Configuration error: {e}")
        raise
    
    except Error as e:
        print(f"Database connection error: {e}")
        raise

db_url = URL.create(
    drivername=os.environ['DB_DRIVER'],
    username=os.environ['DB_USERNAME'],
    password=os.environ['DB_PASSWORD'],
    host=os.environ['DB_HOST'],
    port=os.environ['DB_PORT'],
    database=os.environ['DB_NAME'],
)
print(db_url)

app = Flask(__name__)
CORS(app, expose_headers=['Access-Token', 'Refresh-Token'])
app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY' , 'helloworld')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.environ['JWT_ACCESS_TOKEN_EXPIRES'])
app.config["SQLALCHEMY_DATABASE_URI"] = db_url

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)
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
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT total_appointments, booked_appointments FROM appointments WHERE date= %s', (date,))
            result: Optional[Tuple[int,int]] = cur.fetchone()
            
            if result is None:
                return {
                    "msg": "Invalid date"
                }, 400
                
            print(result)
        totalAppointments, bookedAppointments = result
                
        return {
            "date": date,
            "totalAppointments": totalAppointments,
            "bookedAppointments": bookedAppointments
        }, 200
    finally:
        conn.close()

@app.route("/appointments/add", methods=["POST"])
@jwt_required()
def add_appointment() -> Tuple[Dict[str, Any],int]:
    date=request.args.get("date")
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except (ValueError, TypeError):
        return {"error": "Invalid date format. Use YYYY-MM-DD."}, 400
    conn = get_db_connection()

class Users(db.Model):
    username: Mapped[str] = mapped_column(String(50),unique=True,primary_key=True)
    password: Mapped[str] = mapped_column(String(128), nullable=False)

    def verify_password(self, password):
        self.password


with app.app_context():
    db.create_all()
