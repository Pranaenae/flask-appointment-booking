from logging import StringTemplateStyle
import os 
from typing import Dict, Any, Optional, Tuple
from flask import Flask, request
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
import psycopg2
from psycopg2 import OperationalError, Error
from flask_cors import CORS

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
        # Handle connection-specific errors (e.g., wrong credentials, network issues)
        print(f"Error connecting to the database: {e}")
        raise
    
    except ValueError as e:
        # Handle missing environment variables
        print(f"Configuration error: {e}")
        raise
    
    except Error as e:
        # Catch any other psycopg2-related errors
        print(f"Database connection error: {e}")
        raise

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY' , 'helloworld')
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
