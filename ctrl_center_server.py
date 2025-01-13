import os
import pytz
import base64
from dateutil import parser
from flask import (
    Flask,
    Response,
    render_template_string,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy
import json
import cv2
import time
import numpy as np
from datetime import datetime
from utils.database import (
    database,
    Drone_Status,
    UpSquared_Status,
    Thermal_Camera_Status,
)
from utils.error_code import ERROR_CODE


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f'sqlite:///{os.path.join(basedir, "all_raw_data.db")}?check_same_thread=False'
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

database.init_app(app)

source_paths = ["ipt430m", "ds4025ft"]


class Stream_Temp_Manager:
    def __init__(self):
        self.ipt430m_temp = None
        self.ipt430m_img = None
        self.ds4025ft_temp = None
        self.ds4025ft_img = None

    def set_temp(self, source, temp):
        if source == "ipt430m":
            self.ipt430m_temp = temp
        elif source == "ds4025ft":
            self.ds4025ft_temp = temp

    def get_temp(self, source):
        if source == "ipt430m":
            return self.ipt430m_temp
        elif source == "ds4025ft":
            return self.ds4025ft_temp

    def set_img(self, source, img_base64):
        if img_base64 is not None:
            decoded_img = base64.b64decode(img_base64)
            np_arr = np.frombuffer(decoded_img, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)  # 解碼為 numpy 陣列
        else:
            img = None

        if source == "ipt430m":
            self.ipt430m_img = img
        elif source == "ds4025ft":
            self.ds4025ft_img = img

    def get_img(self, source):
        if source == "ipt430m":
            return self.ipt430m_img
        elif source == "ds4025ft":
            return self.ds4025ft_img


stream_temp_manager = Stream_Temp_Manager()


# ------------------------------- upload status ------------------------------ #


@app.route("/upload/DroneStatus", methods=["POST"])
def upload_drone_status():
    if request.method == "POST":
        if request.is_json:
            data = request.get_json()

            upload_time_str = data.get(
                "upload_time", datetime.now(pytz.timezone("Asia/Taipei")).isoformat()
            )
            upload_time = parser.isoparse(
                upload_time_str
            )  # 將 ISO 8601 格式轉換為 datetime

            sensor_health = data.get("sensor_health")
            battery_voltage = data.get("battery_voltage")
            battery_current = data.get("battery_current")
            battery_remaining = data.get("battery_remaining")
            gps_hdop = data.get("gps_hdop")
            gps_satellites_visible = data.get("gps_satellites_visible")
            attitude_roll = data.get("attitude_roll")
            attitude_pitch = data.get("attitude_pitch")
            attitude_yaw = data.get("attitude_yaw")
            servo_output_1 = data.get("servo_output_1")
            servo_output_2 = data.get("servo_output_2")
            servo_output_3 = data.get("servo_output_3")
            servo_output_4 = data.get("servo_output_4")
            servo_output_5 = data.get("servo_output_5")
            servo_output_6 = data.get("servo_output_6")
            error_code = json.dumps(data.get("error_code", []))  # 將列表轉為 JSON 字串
        else:
            pass

        new_status = Drone_Status(
            upload_time=upload_time,
            sensor_health=sensor_health,
            battery_voltage=battery_voltage,
            battery_current=battery_current,
            battery_remaining=battery_remaining,
            gps_hdop=gps_hdop,
            gps_satellites_visible=gps_satellites_visible,
            attitude_roll=attitude_roll,
            attitude_pitch=attitude_pitch,
            attitude_yaw=attitude_yaw,
            servo_output_1=servo_output_1,
            servo_output_2=servo_output_2,
            servo_output_3=servo_output_3,
            servo_output_4=servo_output_4,
            servo_output_5=servo_output_5,
            servo_output_6=servo_output_6,
            error_code=error_code,
        )

        try:
            database.session.add(new_status)
            database.session.commit()
            return jsonify({"message": "Status added successfully"}), 200

        except Exception as e:
            print(f"資料庫錯誤: {e}")
            return jsonify({"message": "There was an issue adding the status"}), 500


@app.route("/upload/UpSquaredStatus", methods=["POST"])
def upload_up_squared_status():
    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
            upload_time_str = data.get(
                "upload_time", datetime.now(pytz.timezone("Asia/Taipei")).isoformat()
            )
            upload_time = parser.isoparse(
                upload_time_str
            )  # 將 ISO 8601 格式轉換為 datetime
            up_squared_service = data.get("up_squared_service")
            rgb_status = data.get("rgb_status")
            thermal_status = data.get("thermal_status")
            error_code = json.dumps(data.get("error_code", []))

        else:
            pass

        new_status = UpSquared_Status(
            upload_time=upload_time,
            up_squared_service=up_squared_service,
            rgb_status=rgb_status,
            thermal_status=thermal_status,
            error_code=error_code,
        )

        try:
            database.session.add(new_status)
            database.session.commit()
            # ------------------------- database.session.commit() ------------------------ #
            return jsonify({"message": "Status added successfully"}), 200
        except Exception as e:
            print(f"資料庫錯誤: {e}")
            return jsonify({"message": "There was an issue adding the status"}), 500


# todo: 不要每次都寫進資料庫
@app.route("/upload/ThermalCameraStatus", methods=["POST"])
def upload_thermal_camera_status():
    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
            upload_time_str = data.get(
                "upload_time", datetime.now(pytz.timezone("Asia/Taipei")).isoformat()
            )
            upload_time = parser.isoparse(upload_time_str)
            source = data.get("source")
            hot_spot_temp = data.get("hot_spot_temp")
            thermal_img = data.get("thermal_img")
            error_code = json.dumps(data.get("error_code", []))

        new_status = Thermal_Camera_Status(
            upload_time=upload_time,
            source=source,
            hot_spot_temp=hot_spot_temp,
            thermal_img=thermal_img,
            error_code=error_code,
        )

        try:
            database.session.add(new_status)
            database.session.commit()
            return jsonify({"message": "Status added successfully"}), 200
        except Exception as e:
            print(f"資料庫錯誤: {e}")
            return jsonify({"message": "There was an issue adding the status"}), 500


# 即時串流: 溫度, 影像
@app.route("/upload/ThermalCameraStream/<source>", methods=["POST"])
def upload_thermal_camera_stream(source):
    if source not in source_paths:
        return jsonify({"message": "Invalid or missing source"}), 400

    if request.is_json:
        data = request.get_json()
        temp = data.get("hot_spot_temp")
        img_base64 = data.get("thermal_img")

        # 更新溫度和影像數據
        stream_temp_manager.set_temp(source, temp)
        stream_temp_manager.set_img(source, img_base64)

        return jsonify({"message": "Stream updated"}), 200
    else:
        return jsonify({"message": "Invalid JSON data"}), 400


# ---------------------------- show in the browser --------------------------- #
@app.route("/thermal_camera_stream/<source>", methods=["GET"])
def thermal_camera_status(source):
    try:
        latest_img = stream_temp_manager.get_img(source)
        latest_temp = stream_temp_manager.get_temp(source)

        if latest_img is not None and latest_temp is not None:
            formatted_temp = round(float(latest_temp), 4)
            return jsonify({"status": "online", "temperature": formatted_temp}), 200
        else:
            return jsonify({"status": "offline", "temperature": "None"}), 404

    except Exception as e:
        print(f"Error in thermal_camera_stream: {e}")
        return jsonify({"status": "offline", "temperature": "Error"}), 500


def generate_frames(source):
    while True:
        try:
            frame = stream_temp_manager.get_img(source)  # 直接從記憶體讀取影像
            if frame is not None:
                ret, buffer = cv2.imencode(".jpg", frame)
                frame = buffer.tobytes()

                # 生成 MJPEG 格式的串流
                yield (
                    b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                )
            time.sleep(0.1)  # 控制幀率，避免 CPU 過載
        except Exception as e:
            print(f"Error generating frame for {source}: {e}")


@app.route("/video_feed/<source>")
def video_feed(source):
    if source not in source_paths:
        return "Invalid source", 400
    return Response(
        generate_frames(source), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/thermal_content")
def thermal_content():
    return render_template("thermal.html")


@app.route("/drone_data", methods=["GET"])
def drone_data():
    try:
        # 查詢最近 10 筆資料
        recent_statuses = (
            Drone_Status.query.order_by(Drone_Status.upload_time.desc()).limit(24).all()
        )

        # 整理資料為 JSON 格式
        data = [
            {
                "id": status.id,
                "upload_time": status.upload_time.strftime("%Y-%m-%d %H:%M:%S"),
                "sensor_health": status.sensor_health,
                "battery_voltage": status.battery_voltage,
                "battery_current": status.battery_current,
                "battery_remaining": status.battery_remaining,
                "gps_hdop": status.gps_hdop,
                "gps_satellites_visible": status.gps_satellites_visible,
                "attitude_roll": status.attitude_roll,
                "attitude_pitch": status.attitude_pitch,
                "attitude_yaw": status.attitude_yaw,
                "servo_output_1": status.servo_output_1,
                "servo_output_2": status.servo_output_2,
                "servo_output_3": status.servo_output_3,
                "servo_output_4": status.servo_output_4,
                "servo_output_5": status.servo_output_5,
                "servo_output_6": status.servo_output_6,
                "error_code": status.error_code,
            }
            for status in recent_statuses
        ]
        return jsonify(data), 200
    except Exception as e:
        print(f"Error fetching drone data: {e}")
        return jsonify({"message": "Internal server error"}), 500


@app.route("/drone_content")
def drone_content():
    return render_template("drone.html")


@app.route("/ups_data", methods=["GET"])
def ups_data():
    try:
        # 接收分頁參數
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=15, type=int)

        # 查詢總數據量
        total_count = UpSquared_Status.query.count()

        # 查詢指定頁面的資料
        query = UpSquared_Status.query.order_by(UpSquared_Status.upload_time.desc())
        paginated_statuses = query.offset((page - 1) * per_page).limit(per_page).all()

        # 整理數據
        data = [
            {
                "id": status.id,
                "date": status.date.strftime("%Y-%m-%d") if status.date else "N/A",
                # "time": status.time.strftime("%H:%M:%S") if status.time else "N/A",
                "upload_time": status.upload_time.strftime("%H:%M:%S"),
                "up_squared_service": (
                    "Online" if status.up_squared_service else "Offline"
                ),
                "rgb_status": "Active" if status.rgb_status else "Inactive",
                "thermal_status": "Active" if status.thermal_status else "Inactive",
                "error_code": status.error_code if status.error_code else "No Error",
            }
            for status in paginated_statuses
        ]

        # 返回數據
        return jsonify({
            "data": data,
            "pagination": {
                "current_page": page,
                "per_page": per_page,
                "total_count": total_count,
                "total_pages": (total_count + per_page - 1) // per_page
            }
        }), 200
    except Exception as e:
        print(f"Error fetching UP Squared data: {e}")
        return jsonify({"message": "Internal server error"}), 500


@app.route("/ups_content")
def ups_content():
    return render_template("ups.html")


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    with app.app_context():
        database.create_all()  # 創建資料庫和表格
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
