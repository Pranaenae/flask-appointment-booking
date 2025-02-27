from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.engine import URL
import os

class Base(DeclarativeBase):
  pass

db_url = URL.create(
    drivername=os.environ['DB_DRIVER'],
    username=os.environ['DB_USERNAME'],
    password=os.environ['DB_PASSWORD'],
    host=os.environ['DB_HOST'],
    port=os.environ['DB_PORT'],
    database=os.environ['DB_NAME'],
)

db = SQLAlchemy(model_class=Base)