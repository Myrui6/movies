from flask import Blueprint, request, jsonify, session
from database import get_db_connection

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/api/orders', methods=['GET'])
def get_orders():
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "message": "User not logged in"}), 401

        user_id = session['user_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT o.id,
                              u.name AS username,
                              m.name AS movie_name,
                              sc.start_time,
                              h.name AS hall,
                              o.seat_details,
                              o.total_price,
                              o.state,
                              o.reason
                       FROM `order` o
                       JOIN user u ON o.user_id = u.id
                       JOIN schedule sc ON o.schedule_id = sc.id
                       JOIN movie m ON sc.movie_id = m.id
                       JOIN hall h ON sc.hall_id = h.id
                       WHERE o.user_id = %s
                       ORDER BY sc.start_time DESC
                       """, (user_id,))

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
        print(f"Get orders error: {e}")
        return jsonify({"success": False, "message": f"Get orders failed: {str(e)}"})

@orders_bp.route('/api/orders', methods=['POST'])
def create_order():
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "message": "User not logged in"}), 401

        data = request.get_json()
        user_id = session['user_id']
        movie_name = data.get('movie_name')
        start_time = data.get('start_time')
        hall = data.get('hall')
        seat = data.get('seat')
        total_price = data.get('total_price')
        schedule_id = data.get('schedule_id')
        selected_seats = data.get('selected_seats')

        if not all([movie_name, start_time, hall, seat, total_price, schedule_id, selected_seats]):
            return jsonify({"success": False, "message": "Missing required information"})

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
                       INSERT INTO `order` (user_id, schedule_id, seat_details, total_price, state)
                       VALUES (%s, %s, %s, %s, %s)
                       """, (user_id, schedule_id, seat, total_price, 0))

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

        return jsonify({"success": True, "message": "Order created successfully"})

    except Exception as e:
        print(f"Create order error: {e}")
        return jsonify({"success": False, "message": f"Create order failed: {str(e)}"})

@orders_bp.route('/api/orders/<int:order_id>/refund', methods=['POST'])
def apply_refund(order_id):
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "message": "User not logged in"}), 401

        user_id = session['user_id']
        data = request.get_json()
        reason = data.get('reason', '')

        if not reason:
            return jsonify({"success": False, "message": "Refund reason cannot be empty"})

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT id
                       FROM `order`
                       WHERE id = %s
                         AND user_id = %s
                         AND state = 0
                       """, (order_id, user_id))

        order = cursor.fetchone()

        if not order:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Order does not exist or cannot apply for refund"})

        cursor.execute("""
                       UPDATE `order`
                       SET state  = 1,
                           reason = %s
                       WHERE id = %s
                         AND user_id = %s
                       """, (reason, order_id, user_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Refund application submitted successfully"})

    except Exception as e:
        print(f"Apply refund error: {e}")
        return jsonify({"success": False, "message": f"Apply refund failed: {str(e)}"})

@orders_bp.route('/api/orders/filter-options', methods=['GET'])
def get_order_filter_options():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT m.name 
            FROM movie m 
            JOIN schedule sc ON m.id = sc.movie_id 
            JOIN `order` o ON sc.id = o.schedule_id 
            WHERE m.name IS NOT NULL AND m.name != ''
        """)
        movie_names = [row[0] for row in cursor.fetchall()]

        cursor.execute("""
            SELECT DISTINCT DATE(sc.start_time) 
            FROM schedule sc 
            JOIN `order` o ON sc.id = o.schedule_id 
            WHERE sc.start_time IS NOT NULL 
            ORDER BY DATE(sc.start_time) DESC
        """)
        dates = [row[0].strftime('%Y-%m-%d') for row in cursor.fetchall()]

        cursor.execute("""
            SELECT DISTINCT h.name 
            FROM hall h 
            JOIN schedule sc ON h.id = sc.hall_id 
            JOIN `order` o ON sc.id = o.schedule_id 
            WHERE h.name IS NOT NULL AND h.name != ''
        """)
        halls = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "data": {
                "movieNames": movie_names,
                "dates": dates,
                "halls": halls
            }
        })

    except Exception as e:
        print(f"Get filter options error: {e}")
        return jsonify({"success": False, "message": f"Get filter options failed: {str(e)}"})

@orders_bp.route('/api/orders/all', methods=['GET'])
def get_all_orders():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT o.id,
                   u.name AS username,
                   m.name AS movie_name,
                   sc.start_time,
                   h.name AS hall,
                   o.seat_details,
                   o.total_price,
                   o.state,
                   o.reason
            FROM `order` o
            JOIN user u ON o.user_id = u.id
            JOIN schedule sc ON o.schedule_id = sc.id
            JOIN movie m ON sc.movie_id = m.id
            JOIN hall h ON sc.hall_id = h.id
            ORDER BY sc.start_time DESC
        """)

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
        print(f"Get all orders error: {e}")
        return jsonify({"success": False, "message": f"Get orders failed: {str(e)}"})

@orders_bp.route('/api/orders/search', methods=['GET'])
def search_orders():
    try:
        movie_name = request.args.get('movie_name', '')
        start_date = request.args.get('start_date', '')
        hall = request.args.get('hall', '')
        state = request.args.get('state', '')

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT o.id,
                   u.name AS username,
                   m.name AS movie_name,
                   sc.start_time,
                   h.name AS hall,
                   o.seat_details,
                   o.total_price,
                   o.state,
                   o.reason
            FROM `order` o
            JOIN user u ON o.user_id = u.id
            JOIN schedule sc ON o.schedule_id = sc.id
            JOIN movie m ON sc.movie_id = m.id
            JOIN hall h ON sc.hall_id = h.id
            WHERE 1=1
        """
        params = []

        if movie_name:
            query += " AND m.name = %s"
            params.append(movie_name)

        if start_date:
            query += " AND DATE(sc.start_time) = %s"
            params.append(start_date)

        if hall:
            query += " AND h.name = %s"
            params.append(hall)

        if state:
            query += " AND o.state = %s"
            params.append(int(state))

        query += " ORDER BY sc.start_time DESC"

        cursor.execute(query, params)
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
        print(f"Search orders error: {e}")
        return jsonify({"success": False, "message": f"Search orders failed: {str(e)}"})

@orders_bp.route('/api/orders/<int:order_id>/process-refund', methods=['POST'])
def process_refund(order_id):
    try:
        data = request.get_json()
        action = data.get('action')

        if not action:
            return jsonify({"success": False, "message": "Missing action type"})

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT id, state, schedule_id, seat_details
                       FROM `order`
                       WHERE id = %s
                         AND state = 1
                       """, (order_id,))

        order = cursor.fetchone()

        if not order:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Order does not exist or status incorrect"})

        schedule_id = order[2]
        seat_details = order[3]

        if action == 'approve':
            cursor.execute("""
                           UPDATE `order`
                           SET state = 2
                           WHERE id = %s
                           """, (order_id,))

            seats = []
            if seat_details:
                seat_items = seat_details.split(',')
                for seat_item in seat_items:
                    seat_item = seat_item.strip()
                    if '排' in seat_item and '座' in seat_item:
                        try:
                            row_str, col_str = seat_item.replace('座', '').split('排')
                            row = int(row_str.strip())
                            col = int(col_str.strip())
                            seats.append((row, col))
                        except ValueError:
                            print(f"Seat format parse error: {seat_item}")

            for row, col in seats:
                cursor.execute("""
                               UPDATE seat
                               SET state = 0
                               WHERE schedule_id = %s
                                 AND row_num = %s
                                 AND col_num = %s
                                 AND state = 1
                               """, (schedule_id, row, col))

            message = "Refund application approved"
        elif action == 'reject':
            message = "Admin cancelled the operation"

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": message
        })

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        print(f"Process refund error: {e}")
        return jsonify({"success": False, "message": f"Process refund failed: {str(e)}"})