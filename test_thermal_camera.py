from flask import Flask, request, Response, render_template_string
import cv2
import numpy as np
import time

app = Flask(__name__)

# 圖像的共享路徑，作為 Flask 和其他進程之間的通信
image_paths = {
    "ipt430m": "/tmp/ipt430m_thermal_image.jpg",
    "ds4025ft": "/tmp/ds4025ft_thermal_image.jpg"
}

latest_temps = {
    "ipt430m": None,
    "ds4025ft": None
}

@app.route('/upload_image', methods=['POST'])
def upload_image():
    global latest_temps

    source = request.form.get('source')
    if not source or source not in image_paths:
        return "Invalid or missing source", 400

    # 檢查是否有文件
    file = request.files.get('file')
    if file:
        if file.filename == '':
            return "No selected file", 400

        # 將圖像讀入並保存
        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        cv2.imwrite(image_paths[source], img)  # 保存到共享位置
    else:
        print(f"No image uploaded for source: {source}")

    # 接收熱點溫度數據
    latest_temps[source] = request.form.get('hot_spot_temp', None)

    return f"Data from {source} received", 200

# 生成實時幀的函數
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

# Flask 路由設置
@app.route('/video_feed/<source>')
def video_feed(source):
    if source not in image_paths:
        return "Invalid source", 400
    return Response(generate_frames(source), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    # 渲染包含視頻和溫度的網頁
    html_content = """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>Thermal Camera Streams</title>
      </head>
      <body>
        <h1>Thermal Camera Streams</h1>
        
        <h2>IPT430M</h2>
        <img src="/video_feed/ipt430m">
        <h3>Hot Spot Temperature: <span id="temperature_ipt430m">Loading...</span> °C</h3>
        
        <h2>DS4025FT</h2>
        <img src="/video_feed/ds4025ft">
        <h3>Hot Spot Temperature: <span id="temperature_ds4025ft">Loading...</span> °C</h3>

        <script>
          // 定時向伺服器請求最新的溫度數據
          function fetchTemperature(source, elementId) {
              fetch(`/latest_temperature/${source}`)
                  .then(response => response.text())
                  .then(data => {
                      document.getElementById(elementId).innerText = data;
                  })
                  .catch(error => {
                      console.error(`Error fetching temperature for ${source}:`, error);
                      document.getElementById(elementId).innerText = "Error";
                  });
          }

          // 定時更新溫度數據
          setInterval(function() {
              fetchTemperature('ipt430m', 'temperature_ipt430m');
              fetchTemperature('ds4025ft', 'temperature_ds4025ft');
          }, 1000); // 每 1 秒更新一次
        </script>
      </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/latest_temperature/<source>', methods=['GET'])
def latest_temperature(source):
    global latest_temps
    if source not in latest_temps:
        return "Invalid source", 400
    # 返回最新的溫度數據，如果溫度數據為空，顯示 "N/A"
    return str(latest_temps[source]) if latest_temps[source] is not None else "N/A"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
