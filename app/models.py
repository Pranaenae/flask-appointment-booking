from sqlalchemy.orm import  Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from .database import db
import datetime

class Users(db.Model):
    username: Mapped[str] = mapped_column(db.String(49),unique=True,primary_key=True)
    password: Mapped[str] = mapped_column(db.String(127), nullable=False)

    user_appointments: Mapped[list['UserAppointments']] = relationship(back_populates='user', cascade='all, delete-orphan')
    def verify_password(self, password):
        pass

    def can_book_appointment(self):
        date = datetime.date.today()
        for appointment in self.user_appointments:
            print(f"Appointment dates: {appointment.date}")
            if appointment.date >= date:
                return False
        return True
    
    def book_appointment(self, appointment_date):
        if not self.can_book_appointment():
            return {"msg": "You already have an active appointment. Cannot book another one."}, 400
        appointment = Appointments.query.get(appointment_date)
        appointment.booked_appointments += 1
        db.session.add(appointment)

        user_appointment = UserAppointments(
            date = appointment_date,
            username = self.username
        )
        db.session.add(user_appointment)
        db.session.commit()

        return {
                "msg": f"Added appointment for date {appointment_date}",
                "totalAppointments": appointment.total_appointments,
                "bookedAppointments": appointment.booked_appointments
        }, 200

class UserAppointments(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime.date] = mapped_column(db.Date, db.ForeignKey('appointments.date'), nullable=False)
    username: Mapped[str] = mapped_column(db.String(49), db.ForeignKey('users.username'), nullable=False)

    user: Mapped['Users'] = relationship(back_populates='user_appointments')
    appointment: Mapped['Appointments'] = relationship(back_populates='user_appointments')
        
class Appointments(db.Model):
    date: Mapped[datetime.date] = mapped_column(db.Date, primary_key=True)
    total_appointments: Mapped[int] = mapped_column(db.Integer, nullable=False)
    booked_appointments: Mapped[int] = mapped_column(db.Integer, nullable=False)

    user_appointments: Mapped[list['UserAppointments']] = relationship(back_populates='appointment')