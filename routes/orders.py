from flask import Blueprint, request, jsonify, session  # 添加session导入
from database import get_db_connection

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/api/orders', methods=['GET'])
def get_orders():
    try:
        # 从session获取用户名，而不是URL参数
        if 'username' not in session:
            return jsonify({"success": False, "message": "用户未登录"}), 401

        username = session['username']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT id,
                              username,
                              movie_name,
                              start_time,
                              hall,
                              seat,
                              total_price,
                              state,
                              reason
                       FROM `order`
                       WHERE username = %s
                       ORDER BY start_time DESC
                       """, (username,))

        orders = cursor.fetchall()
        cursor.close()
        conn.close()

        order_list = []
        for order in orders:
            order_list.append({
                'id': order[0],
                'username': order[1],
                'movie_name': order[2],
                'start_time': order[3].strftime('%Y-%m-%d %H:%M:%S') if order[3] else '',
                'hall': order[4],
                'seat': order[5],
                'total_price': order[6],
                'state': order[7],
                'reason': order[8]
            })

        return jsonify({"success": True, "data": order_list})

    except Exception as e:
        print(f"获取订单错误: {e}")
        return jsonify({"success": False, "message": f"获取订单失败: {str(e)}"})


@orders_bp.route('/api/orders', methods=['POST'])
def create_order():
    try:
        # 从session获取用户名
        if 'username' not in session:
            return jsonify({"success": False, "message": "用户未登录"}), 401

        data = request.get_json()
        username = session['username']  # 从session获取
        movie_name = data.get('movie_name')
        start_time = data.get('start_time')
        hall = data.get('hall')
        seat = data.get('seat')
        total_price = data.get('total_price')
        schedule_id = data.get('schedule_id')
        selected_seats = data.get('selected_seats')

        if not all([movie_name, start_time, hall, seat, total_price, schedule_id, selected_seats]):
            return jsonify({"success": False, "message": "缺少必要信息"})

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
                       INSERT INTO `order` (username, movie_name, start_time, hall, seat, total_price, state)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)
                       """, (username, movie_name, start_time, hall, seat, total_price, 0))

        for seat_info in selected_seats:
            cursor.execute("""
                           UPDATE seat
                           SET state = 1
                           WHERE schedule_id = %s
                             AND row_num = %s
                             AND col_num = %s
                           """, (schedule_id, seat_info['row'], seat_info['col']))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "订单创建成功"})

    except Exception as e:
        print(f"创建订单错误: {e}")
        return jsonify({"success": False, "message": f"创建订单失败: {str(e)}"})


# 新增：更新订单状态接口
@orders_bp.route('/api/orders/<int:order_id>/refund', methods=['POST'])
def apply_refund(order_id):
    try:
        # 从session获取用户名
        if 'username' not in session:
            return jsonify({"success": False, "message": "用户未登录"}), 401

        username = session['username']
        data = request.get_json()
        reason = data.get('reason', '')

        if not reason:
            return jsonify({"success": False, "message": "退票原因不能为空"})

        conn = get_db_connection()
        cursor = conn.cursor()

        # 验证订单属于当前用户且状态为0（已完成）
        cursor.execute("""
                       SELECT id
                       FROM `order`
                       WHERE id = %s
                         AND username = %s
                         AND state = 0
                       """, (order_id, username))

        order = cursor.fetchone()

        if not order:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "订单不存在或无法申请退票"})

        # 更新订单状态和原因
        cursor.execute("""
                       UPDATE `order`
                       SET state  = 1,
                           reason = %s
                       WHERE id = %s
                         AND username = %s
                       """, (reason, order_id, username))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "退票申请提交成功"})

    except Exception as e:
        print(f"申请退票错误: {e}")
        return jsonify({"success": False, "message": f"申请退票失败: {str(e)}"})