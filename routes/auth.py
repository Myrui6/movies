from flask import Blueprint, request, jsonify, session
from database import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user_type = data.get('userType')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password cannot be empty"})

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
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['user_type'] = user_type

            return jsonify({
                "success": True,
                "message": "Login successful",
                "user": {
                    "id": user[0],
                    "username": user[1],
                    "type": user_type
                },
                "redirect": "/home" if user_type == "员工" else "/user-buy"
            })
        else:
            return jsonify({"success": False, "message": f"{user_table} account or password error"})

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"success": False, "message": f"Login failed: {str(e)}"})

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user_type = data.get('userType')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password cannot be empty"})

    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters"})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if user_type == '员工':
            cursor.execute("SELECT id FROM administrator WHERE name = %s", (username,))
            table_name = "administrator"
        else:
            cursor.execute("SELECT id FROM user WHERE name = %s", (username,))
            table_name = "user"

        existing_user = cursor.fetchone()
        if existing_user:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": f"Username '{username}' already exists"})

        if user_type == '员工':
            cursor.execute("INSERT INTO administrator (name, password) VALUES (%s, %s)",
                           (username, password))
        else:
            cursor.execute("INSERT INTO user (name, password) VALUES (%s, %s)",
                           (username, password))

        conn.commit()
        user_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": f"{user_type} registration successful",
            "user": {
                "id": user_id,
                "username": username,
                "type": user_type
            }
        })

    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({"success": False, "message": f"Registration failed: {str(e)}"})

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
            "message": "User not logged in"
        }), 401

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({
        "success": True,
        "message": "Logout successful"
    })