from sqlalchemy.orm import  Mapped, mapped_column
from database import db
import datetime

class Users(db.Model):
    username: Mapped[str] = mapped_column(db.String(49),unique=True,primary_key=True)
    password: Mapped[str] = mapped_column(db.String(127), nullable=False)

    def verify_password(self, password):
        self.password


class Appointments(db.Model):
    date: Mapped[datetime.date] = mapped_column(db.Date, primary_key=True)
    total_appointments: Mapped[int] = mapped_column(db.Column(db.Integer, nullable=False))
    booked_appointments: Mapped[int] = mapped_column(db.Column(db.Integer, nullable=False))