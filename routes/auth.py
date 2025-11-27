from flask import Blueprint, request, jsonify, session  # 添加session导入
from database import get_db_connection

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user_type = data.get('userType')

    if not username or not password:
        return jsonify({"success": False, "message": "用户名和密码不能为空"})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if user_type == '员工':
            cursor.execute("SELECT id, name FROM administrator WHERE name = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            user_table = "administrator"
        else:
            cursor.execute("SELECT id, name FROM user WHERE name = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            user_table = "user"

        cursor.close()
        conn.close()

        if user:
            # 设置session - 新增代码
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['user_type'] = user_type

            return jsonify({
                "success": True,
                "message": "登录成功",
                "user": {
                    "id": user[0],
                    "username": user[1],
                    "type": user_type
                },
                "redirect": "/home" if user_type == "员工" else "/user-buy"
            })
        else:
            return jsonify({"success": False, "message": f"{user_table}账号或密码错误"})

    except Exception as e:
        print(f"登录错误: {e}")
        return jsonify({"success": False, "message": f"登录失败: {str(e)}"})


# 新增获取当前用户信息的接口
@auth_bp.route('/api/current-user', methods=['GET'])
def get_current_user():
    if 'username' in session:
        return jsonify({
            "success": True,
            "data": {
                "id": session['user_id'],
                "username": session['username'],
                "type": session['user_type']
            }
        })
    else:
        return jsonify({
            "success": False,
            "message": "用户未登录"
        }), 401


# 新增退出登录接口
@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({
        "success": True,
        "message": "退出登录成功"
    })