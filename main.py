from logging import StringTemplateStyle
import os 
from typing import Dict, Any, Optional, Tuple
from flask import Flask, request
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
import psycopg2
from flask_cors import CORS

def get_db_connection():
    return psycopg2.connect(
    host=os.environ['DB_HOST'],
    database=os.environ['DB_NAME'],
    user=os.environ['DB_USERNAME'],
    password=os.environ['DB_PASSWORD'],
)

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = os.environ['JWT_SECRET_KEY']
jwt = JWTManager(app)
@app.route("/")
def ping() -> Tuple [str, int]:
    return "App is running", 200
@app.route('/login', methods=['POST'])
def login() -> Tuple[Dict[str, Any],Any]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            print(username, password)
            
            cur.execute('SELECT password FROM accounts WHERE username = %s', (username,))
            result: Optional[Tuple[str,]] = cur.fetchone()
            
            if result is None:
                return {
                    "msg": "Invalid credentials"
                }, 400
                
            print(result[0])
            if password != result[0]:
                return {
                    "msg": "Invalid credentials"
                }, 400
                
            access_token = create_access_token(identity=username)
            return {
                "access_token": access_token
            }, 200
    finally:
        conn.close()

@app.route("/protected", methods=["GET"])
@jwt_required()
def protected()-> Tuple[Dict[str, Any],Any]:
    current_user= get_jwt_identity()
    return {
        "logged_in_as": current_user
    },200
