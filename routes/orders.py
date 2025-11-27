from flask import Blueprint, request, jsonify
from database import get_db_connection

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        username = data.get('username')
        movie_name = data.get('movie_name')
        start_time = data.get('start_time')
        hall = data.get('hall')
        seat = data.get('seat')
        total_price = data.get('total_price')
        schedule_id = data.get('schedule_id')
        selected_seats = data.get('selected_seats')

        # 验证必填字段
        if not all([username, movie_name, start_time, hall, seat, total_price, schedule_id, selected_seats]):
            return jsonify({"success": False, "message": "缺少必要信息"})

        conn = get_db_connection()
        cursor = conn.cursor()

        # 插入订单信息
        cursor.execute("""
            INSERT INTO `order` (username, movie_name, start_time, hall, seat, total_price, state) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (username, movie_name, start_time, hall, seat, total_price, 0))

        # 更新座位状态为已售出
        for seat_info in selected_seats:
            cursor.execute("""
                UPDATE seat 
                SET state = 1 
                WHERE schedule_id = %s AND row_num = %s AND col_num = %s
            """, (schedule_id, seat_info['row'], seat_info['col']))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "订单创建成功"})

    except Exception as e:
        print(f"创建订单错误: {e}")
        return jsonify({"success": False, "message": f"创建订单失败: {str(e)}"})


@orders_bp.route('/api/orders', methods=['GET'])
def get_orders():
    try:
        username = request.args.get('username')

        if not username:
            return jsonify({"success": False, "message": "缺少用户名"})

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

        # 转换结果为字典列表
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