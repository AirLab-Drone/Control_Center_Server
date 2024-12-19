import pytz
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

database = SQLAlchemy()


'''
database 有三個table
    1. 飛控狀態 
    2. up squared 狀態 (RGB, Thermal) 
    3. 環境熱像儀狀態
''' 




class Drone_Status(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    date = database.Column(
        database.Date, default=datetime.now(pytz.timezone("Asia/Taipei")).date()
    )
    time = database.Column(
        database.Time,
        default=lambda: datetime.now(pytz.timezone("Asia/Taipei"))
        .time(),
    )

    upload_time = database.Column(database.DateTime, nullable=False)
    mavlink_status = database.Column(database.String(255), nullable=True)
    sensor_health = database.Column(database.Integer, nullable=True)
    battery_voltage = database.Column(database.Float, nullable=True)
    battery_current = database.Column(database.Float, nullable=True)
    battery_remaining = database.Column(database.Integer, nullable=True)
    gps_hdop = database.Column(database.Float, nullable=True)
    gps_satellites_visible = database.Column(database.Integer, nullable=True)
    attitude_roll = database.Column(database.Float, nullable=True)
    attitude_pitch = database.Column(database.Float, nullable=True)
    attitude_yaw = database.Column(database.Float, nullable=True)
    servo_output_1 = database.Column(database.Integer, nullable=True)
    servo_output_2 = database.Column(database.Integer, nullable=True)
    servo_output_3 = database.Column(database.Integer, nullable=True)
    servo_output_4 = database.Column(database.Integer, nullable=True)
    servo_output_5 = database.Column(database.Integer, nullable=True)
    servo_output_6 = database.Column(database.Integer, nullable=True)
    error_code = database.Column(database.String(255), nullable=True)

    def __repr__(self):
        return f"<Drone_Status {self.id}>"




class UpSquared_Status(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    date = database.Column(
        database.Date, default=datetime.now(pytz.timezone("Asia/Taipei")).date()
    )
    time = database.Column(
        database.Time,
        default=lambda: datetime.now(pytz.timezone("Asia/Taipei")).time(),
    )

    upload_time = database.Column(database.DateTime, nullable=False)

    up_squared_service = database.Column(database.Boolean, nullable=True)
    rgb_status = database.Column(database.Boolean, nullable=True)
    thermal_status = database.Column(database.Boolean, nullable=True)
    error_code = database.Column(database.String(255), nullable=True)

    def __repr__(self):
        return f"<UpSquared_Status {self.id}>"
    





class Thermal_Camera_Status(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    date = database.Column(
        database.Date, default=datetime.now(pytz.timezone("Asia/Taipei")).date()
    )
    time = database.Column(
        database.Time,
        default=lambda: datetime.now(pytz.timezone("Asia/Taipei")).time(),
    )
    upload_time = database.Column(database.DateTime, nullable=False)
    source = database.Column(database.String(255), nullable=True)
    hot_spot_temp = database.Column(database.Float, nullable=True)
    thermal_img = database.Column(database.Boolean, nullable=True)
    error_code = database.Column(database.String(255), nullable=True)

    def __repr__(self):
        return f"<Thermal_Camera_Status {self.id}>"