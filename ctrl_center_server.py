import os
import pytz
import base64
from dateutil import parser
from flask import Flask,Response, render_template_string, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
import cv2
import time
from datetime import datetime
from utils.database import database, Drone_Status, UpSquared_Status, Thermal_Camera_Status
from utils.error_code import ERROR_CODE


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{os.path.join(basedir, "all_raw_data.db")}?check_same_thread=False'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

database.init_app(app)

image_paths = {
    "ipt430m": "/tmp/ipt430m_thermal_image.jpg",
    "ds4025ft": "/tmp/ds4025ft_thermal_image.jpg"
}



# ------------------------------- upload status ------------------------------ #

@app.route("/upload/DroneStatus", methods=["POST"])
def upload_drone_status():
    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
            
            upload_time_str = data.get("upload_time", datetime.now(pytz.timezone("Asia/Taipei")).isoformat())
            upload_time = parser.isoparse(upload_time_str)  # 將 ISO 8601 格式轉換為 datetime
            
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
            return jsonify(
                {"message": "There was an issue adding the status"}
            ), 500





@app.route("/upload/UpSquaredStatus", methods=["POST"])
def upload_up_squared_status():
    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
            upload_time_str = data.get("upload_time", datetime.now(pytz.timezone("Asia/Taipei")).isoformat())
            upload_time = parser.isoparse(upload_time_str)  # 將 ISO 8601 格式轉換為 datetime
            up_squared_service = data.get("up_squared_service")
            rgb_status = data.get("rgb_status")
            thermal_status = data.get("thermal_status")
            error_code = json.dumps(data.get("error_code", []))


        else:
            pass

        new_status = UpSquared_Status(
            upload_time=upload_time,
            up_squared_service = up_squared_service,
            rgb_status = rgb_status,
            thermal_status = thermal_status,
            error_code = error_code,
        )

        try:
            database.session.add(new_status)
            database.session.commit()
            return jsonify({"message": "Status added successfully"}), 200
        except Exception as e:
            print(f"資料庫錯誤: {e}")
            return jsonify(
                {"message": "There was an issue adding the status"}
            ), 500





@app.route("/upload/ThermalCameraStatus", methods=["POST"])
def upload_thermal_camera_status():
    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
            upload_time_str = data.get("upload_time", datetime.now(pytz.timezone("Asia/Taipei")).isoformat())
            upload_time = parser.isoparse(upload_time_str)
            source = data.get("source")
            hot_spot_temp = data.get("hot_spot_temp")
            thermal_img = data.get("thermal_img")
            error_code = json.dumps(data.get("error_code", []))

            if thermal_img is not None:
                is_thermal_img = True
                try:
                    decoded_img = base64.b64decode(thermal_img)
                    if source not in image_paths:
                        return jsonify({"message": "Invalid or missing source"}), 400
                    else:
                        with open(image_paths[source], "wb") as f:
                            f.write(decoded_img)
                except Exception as e:
                    return jsonify({"message": f"Error decoding image: {e}"}), 400

            else:
                is_thermal_img = False
                
        else:
            pass

        new_status = Thermal_Camera_Status(
            upload_time=upload_time,
            source = source,
            hot_spot_temp = hot_spot_temp,
            thermal_img = is_thermal_img,
            error_code = error_code,
        )

        try:
            database.session.add(new_status)
            database.session.commit()
            return jsonify({"message": "Status added successfully"}), 200
        except Exception as e:
            print(f"資料庫錯誤: {e}")
            return jsonify(
                {"message": "There was an issue adding the status"}
            ), 500
        



# ---------------------------- show in the browser --------------------------- #
@app.route('/thermal_camera_status/<source>', methods=["GET"])
def thermal_camera_status(source):
    try:
        # print(f"Received request for thermal camera status: {source}")
        # 從資料庫獲取最新資料
        latest_status = Thermal_Camera_Status.query.filter_by(source=source).order_by(
            Thermal_Camera_Status.upload_time.desc()
        ).first()

        if not latest_status:
            return jsonify({"status": "offline", "message": "No data available"}), 404

        if latest_status.thermal_img:
            return jsonify({"status": "online", "message": "Thermal camera is good"}), 200
        else:
            return jsonify({"status": "offline", "message": "Thermal camera error"}), 200
    except Exception as e:
        print(f"Error in thermal_camera_status: {e}")
        return jsonify({"status": "offline", "message": "Internal server error"}), 500

# todo: 把影像跟溫度開一個路由 然後不要寫進資料庫



def generate_frames(source):
    while True:
        try:
            # 從共享路徑讀取圖片
            frame = cv2.imread(image_paths[source])
            if frame is not None:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                # 生成 MJPEG 格式的串流
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.05)  # 控制幀率
        except Exception as e:
            print(f"Error generating frame for {source}: {e}")

@app.route('/video_feed/<source>')
def video_feed(source):
    if source not in image_paths:
        return "Invalid source", 400
    return Response(generate_frames(source), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/latest_temperature/<source>', methods=["GET"])
def latest_temperature(source):
    try:
        # print(f"Received request for latest temperature: {source}")
        latest_status = Thermal_Camera_Status.query.filter_by(source=source).order_by(
            Thermal_Camera_Status.upload_time.desc()
        ).first()

        if latest_status and latest_status.hot_spot_temp is not None:
            formatted_temp = round(float(latest_status.hot_spot_temp), 4)
            return jsonify({"temperature": formatted_temp}), 200
        else:
            return jsonify({"temperature": "None"}), 200
    except Exception as e:
        print(f"Error fetching temperature: {e}")
        return jsonify({"message": "Internal server error"}), 500
    

@app.route("/thermal_content")
def thermal_content():
    return render_template("thermal.html")




@app.route("/drone_data", methods=["GET"])
def drone_data():
    try:
        # 查詢最近 10 筆資料
        recent_statuses = Drone_Status.query.order_by(Drone_Status.upload_time.desc()).limit(24).all()

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


@app.route("/")
def index():
    return render_template("index.html")

















# # 生成實時幀的函數
# def generate_frames(source):
#     while True:
#         try:
#             # 從共享路徑讀取圖片
#             frame = cv2.imread(image_paths[source])
#             if frame is not None:
#                 ret, buffer = cv2.imencode('.jpg', frame)
#                 frame = buffer.tobytes()
#                 # 生成 MJPEG 格式的串流
#                 yield (b'--frame\r\n'
#                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#             time.sleep(0.05)  # 控制幀率
#         except Exception as e:
#             print(f"Error generating frame for {source}: {e}")

# # Flask 路由設置
# @app.route('/video_feed/<source>')
# def video_feed(source):
#     if source not in image_paths:
#         return "Invalid source", 400
#     return Response(generate_frames(source), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/')
# def index():
#     # 渲染包含視頻和溫度的網頁
#     html_content = """
#     <!doctype html>
#     <html lang="en">
#       <head>
#         <meta charset="utf-8">
#         <title>Thermal Camera Streams</title>
#       </head>
#       <body>
#         <h1>Thermal Camera Streams</h1>
        
#         <h2>IPT430M</h2>
#         <img src="/video_feed/ipt430m">
#         <h3>Hot Spot Temperature: <span id="temperature_ipt430m">Loading...</span> °C</h3>
        
#         <h2>DS4025FT</h2>
#         <img src="/video_feed/ds4025ft">
#         <h3>Hot Spot Temperature: <span id="temperature_ds4025ft">Loading...</span> °C</h3>

#         <script>
#           // 定時向伺服器請求最新的溫度數據
#           function fetchTemperature(source, elementId) {
#               fetch(`/latest_temperature/${source}`)
#                   .then(response => response.text())
#                   .then(data => {
#                       document.getElementById(elementId).innerText = data;
#                   })
#                   .catch(error => {
#                       console.error(`Error fetching temperature for ${source}:`, error);
#                       document.getElementById(elementId).innerText = "Error";
#                   });
#           }

#           // 定時更新溫度數據
#           setInterval(function() {
#               fetchTemperature('ipt430m', 'temperature_ipt430m');
#               fetchTemperature('ds4025ft', 'temperature_ds4025ft');
#           }, 1000); // 每 1 秒更新一次
#         </script>
#       </body>
#     </html>
#     """
#     return render_template_string(html_content)








# 刪除電池狀態的路由
@app.route("/delete/<int:id>")
def delete(id):
    status_to_delete = Drone_Status.query.get_or_404(id)

    try:
        database.session.delete(status_to_delete)
        database.session.commit()
        return redirect("/")
    except Exception as e:
        print(f"刪除錯誤: {e}")
        return "There was a problem deleting that status"

# 更新電池狀態的路由
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    status = Drone_Status.query.get_or_404(id)

    if request.method == "POST":
        status.sensor_health = request.form["sensor_health"]
        status.battery_voltage = request.form["battery_voltage"]
        status.battery_current = request.form["battery_current"]
        status.battery_remaining = request.form["battery_remaining"]
        status.gps_hdop = request.form["gps_hdop"]
        status.gps_satellites_visible = request.form["gps_satellites_visible"]
        status.attitude_roll = request.form["attitude_roll"]
        status.attitude_pitch = request.form["attitude_pitch"]
        status.attitude_yaw = request.form["attitude_yaw"]
        status.servo_output_1 = request.form["servo_output_1"]
        status.servo_output_2 = request.form["servo_output_2"]
        status.servo_output_3 = request.form["servo_output_3"]
        status.servo_output_4 = request.form["servo_output_4"]
        status.servo_output_5 = request.form["servo_output_5"]
        status.servo_output_6 = request.form["servo_output_6"]
        try:
            database.session.commit()
            return redirect(url_for("index", updated="true"))
        except Exception as e:
            print(f"更新錯誤: {e}")
            return "There was an issue updating the status"
    else:
        return render_template("update.html", status=status)

# 取得所有狀態資料 (JSON 格式)
@app.route("/api/statuses", methods=["GET"])
def get_statuses():
    statuses = Drone_Status.query.order_by(Drone_Status.id).all()
    return jsonify(
        [
            {
                "id": status.id,
                "timestamp": status.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
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
            }
            for status in statuses
        ]
    )

if __name__ == "__main__":
    with app.app_context():
        database.create_all()  # 創建資料庫和表格
    app.run(debug=True, host='0.0.0.0', port=5000)
