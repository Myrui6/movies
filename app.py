from flask import Flask, send_from_directory
from flask_cors import CORS
from routes.auth import auth_bp
from routes.movies import movies_bp
from routes.schedules import schedules_bp  # 新增导入
from routes.seats import seats_bp
from routes.orders import orders_bp  # 新增导入

import os

app = Flask(__name__)
CORS(app)

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(movies_bp)
app.register_blueprint(schedules_bp)
app.register_blueprint(seats_bp) # 新增注册
# 注册蓝图
app.register_blueprint(orders_bp)  # 新增注册

# 创建上传目录
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 静态文件路由
@app.route('/')
def home():
    return send_from_directory('frontend/html', 'login.html')

@app.route('/home')
def home_page():
    return send_from_directory('frontend/html', 'movie_schedule_management.html')

@app.route('/add-movie')
def add_movie():
    return send_from_directory('frontend/html', 'add_movie.html')

@app.route('/css/<filename>')
def css(filename):
    return send_from_directory('frontend/css', filename)

@app.route('/js/<filename>')
def js(filename):
    return send_from_directory('frontend/js', filename)

# 提供上传文件的访问
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/movie-schedule-detail')
def movie_schedule_detail():
    return send_from_directory('frontend/html', 'movie_schedule_detail.html')

@app.route('/add-schedule')
def add_schedule():
    return send_from_directory('frontend/html', 'add_schedule.html')

@app.route('/user-buy')
def user_buy():
    return send_from_directory('frontend/html', 'user_buy.html')

@app.route('/choose-schedule')
def choose_schedule():
    return send_from_directory('frontend/html', 'choose_schedule.html')

@app.route('/choose-seat')
def choose_seat():
    return send_from_directory('frontend/html', 'choose_seat.html')

@app.route('/my-order')
def my_order():
    return send_from_directory('frontend/html', 'my_order.html')


if __name__ == '__main__':
    print(f"上传目录: {UPLOAD_FOLDER}")
    app.run(debug=True, port=5000)