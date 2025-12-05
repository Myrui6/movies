from flask import Blueprint, request, jsonify
from database import get_db_connection
from datetime import datetime

schedules_bp = Blueprint('schedules', __name__)

@schedules_bp.route('/api/schedules/<int:schedule_id>', methods=['GET'])
def get_schedule_detail(schedule_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT 
                           t1.start_time, t1.price, 
                           t2.name AS movie_name, 
                           t3.name AS hall_name, t3.total_rows, t3.total_columns
                       FROM schedule t1
                       JOIN movie t2 ON t1.movie_id = t2.id
                       JOIN hall t3 ON t1.hall_id = t3.id
                       WHERE t1.id = %s
                       """, (schedule_id,))
        schedule = cursor.fetchone()

        cursor.close()
        conn.close()

        if not schedule:
            return jsonify({"success": False, "message": "Schedule not found"})

        schedule_dict = {
            'start_time': schedule[0].strftime('%Y-%m-%d %H:%M:%S') if schedule[0] else '',
            'price': float(schedule[1]) if schedule[1] else 0,
            'movie_name': schedule[2],
            'hall': schedule[3],
            'seat_rows': schedule[4],
            'seat_columns': schedule[5]
        }

        return jsonify({"success": True, "data": schedule_dict})

    except Exception as e:
        print(f"Get schedule detail error: {e}")
        return jsonify({"success": False, "message": f"Failed to get schedule: {str(e)}"})

@schedules_bp.route('/api/schedules', methods=['GET'])
def get_schedules():
    try:
        movie_id = request.args.get('movie_id')

        conn = get_db_connection()
        cursor = conn.cursor()

        if movie_id:
            cursor.execute(
                "SELECT id, movie_name, start_time, hall, price, seat_rows, seat_columns FROM schedule WHERE movie_id = %s",
                (movie_id,))
        else:
            cursor.execute("SELECT id, movie_name, start_time, hall, price, seat_rows, seat_columns FROM schedule")

        schedules = cursor.fetchall()
        cursor.close()
        conn.close()

        schedule_list = []
        for schedule in schedules:
            schedule_list.append({
                'id': schedule[0],
                'movie_name': schedule[1],
                'start_time': schedule[2].strftime('%Y-%m-%d %H:%M:%S') if schedule[2] else '',
                'hall': schedule[3],
                'price': float(schedule[4]) if schedule[4] else 0,
                'seat_rows': schedule[5],
                'seat_columns': schedule[6]
            })

        return jsonify({"success": True, "data": schedule_list})

    except Exception as e:
        print(f"Get schedules error: {e}")
        return jsonify({"success": False, "message": f"Failed to get schedules: {str(e)}"})

@schedules_bp.route('/api/schedules/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM seat WHERE schedule_id = %s", (schedule_id,))
        deleted_seats_count = cursor.fetchone()[0]

        cursor.execute("DELETE FROM schedule WHERE id = %s", (schedule_id,))

        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"success": False, "message": "Schedule not found"})

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": f"Schedule deleted successfully! Cleaned up {deleted_seats_count} seats and related order records."})

    except Exception as e:
        conn.rollback()
        print(f"Delete schedule error: {e}")
        return jsonify({"success": False, "message": f"Failed to delete schedule: {str(e)}"})

@schedules_bp.route('/api/schedules', methods=['POST'])
def add_schedule():
    data = request.get_json()
    movie_id = data.get('movie_id')
    hall_id = data.get('hall_id')
    start_time = data.get('start_time')
    price = data.get('price')

    if not all([movie_id, hall_id, start_time, price]):
        return jsonify({"success": False, "message": "Please fill all required fields"})

    try:
        movie_id = int(movie_id)
        hall_id = int(hall_id)
        price = float(price)
    except ValueError:
        return jsonify({"success": False, "message": "Movie ID, Hall ID and Price must be valid numbers"})

    conn = get_db_connection()
    cursor = conn.cursor()
    schedule_id = None
    seat_data = []

    try:
        cursor.execute("SELECT name, total_rows, total_columns FROM hall WHERE id = %s", (hall_id,))
        hall_info = cursor.fetchone()

        if not hall_info:
            return jsonify({"success": False, "message": f"Hall ID '{hall_id}' does not exist"})

        seat_rows = hall_info[1]
        seat_columns = hall_info[2]

        cursor.execute("""
                       INSERT INTO schedule (movie_id, hall_id, start_time, price)
                       VALUES (%s, %s, %s, %s)
                       """, (movie_id, hall_id, start_time, price))

        schedule_id = cursor.lastrowid

        for row in range(1, seat_rows + 1):
            for col in range(1, seat_columns + 1):
                seat_data.append((schedule_id, row, col, 0))

        if seat_data:
            cursor.executemany("""
                               INSERT INTO seat (schedule_id, row_num, col_num, state)
                               VALUES (%s, %s, %s, %s)
                               """, seat_data)

        conn.commit()
        return jsonify({"success": True, "message": f"Schedule added successfully! Automatically generated {len(seat_data)} seats."})

    except Exception as e:
        conn.rollback()
        print(f"Add schedule error: {e}")
        return jsonify({"success": False, "message": f"Add failed: {str(e)}"})
    finally:
        cursor.close()
        conn.close()

@schedules_bp.route('/api/schedules', methods=['GET'])
def get_all_schedules():
    return jsonify({"success": False, "message": "This API is not implemented or enabled"})

@schedules_bp.route('/api/schedules/movie/<int:movie_id>', methods=['GET'])
def get_schedules_by_movie(movie_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT t1.id,
                              t1.start_time,
                              t1.price,
                              t2.name AS movie_name,
                              t3.name AS hall_name
                       FROM schedule t1
                                JOIN movie t2 ON t1.movie_id = t2.id
                                JOIN hall t3 ON t1.hall_id = t3.id
                       WHERE t1.movie_id = %s
                       ORDER BY t1.start_time
                       """, (movie_id,))
        schedules = cursor.fetchall()

        cursor.close()
        conn.close()

        schedule_list = []
        for sch in schedules:
            schedule_list.append({
                'id': sch[0],
                'start_time': sch[1].strftime('%Y-%m-%d %H:%M:%S') if sch[1] else '',
                'price': float(sch[2]),
                'movie_name': sch[3],
                'hall': sch[4]
            })

        return jsonify({"success": True, "data": schedule_list})

    except Exception as e:
        print(f"Get movie schedules error: {e}")
        return jsonify({"success": False, "message": f"Failed to get schedules: {str(e)}"})