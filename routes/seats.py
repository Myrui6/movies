from flask import Blueprint, request, jsonify
from database import get_db_connection

seats_bp = Blueprint('seats', __name__)

@seats_bp.route('/api/seats', methods=['GET'])
def get_seats():
    try:
        schedule_id = request.args.get('schedule_id')

        if not schedule_id:
            return jsonify({"success": False, "message": "Missing schedule ID"})

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT row_num, col_num, state FROM seat WHERE schedule_id = %s", (schedule_id,))
        seats = cursor.fetchall()

        cursor.close()
        conn.close()

        seat_list = []
        for seat in seats:
            seat_list.append({
                'row_num': seat[0],
                'col_num': seat[1],
                'state': seat[2]
            })

        return jsonify({"success": True, "data": seat_list})

    except Exception as e:
        print(f"Get seats error: {e}")
        return jsonify({"success": False, "message": f"Get seats failed: {str(e)}"})

@seats_bp.route('/api/seats/lock', methods=['POST'])
def lock_seat():
    try:
        data = request.get_json()
        schedule_id = data.get('schedule_id')
        row_num = data.get('row')
        col_num = data.get('col')

        if not all([schedule_id, row_num, col_num]):
            return jsonify({"success": False, "message": "Missing required parameters"})

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT state FROM seat 
            WHERE schedule_id = %s AND row_num = %s AND col_num = %s
            FOR UPDATE
        """, (schedule_id, row_num, col_num))

        seat = cursor.fetchone()

        if not seat:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Seat does not exist"})

        if seat[0] != 0:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Seat not available"})

        cursor.execute("""
            UPDATE seat 
            SET state = 2 
            WHERE schedule_id = %s AND row_num = %s AND col_num = %s
        """, (schedule_id, row_num, col_num))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Seat locked successfully"})

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        print(f"Lock seat error: {e}")
        return jsonify({"success": False, "message": f"Lock seat failed: {str(e)}"})

@seats_bp.route('/api/seats/release', methods=['POST'])
def release_seat():
    try:
        data = request.get_json()
        schedule_id = data.get('schedule_id')
        row_num = data.get('row')
        col_num = data.get('col')

        if not all([schedule_id, row_num, col_num]):
            return jsonify({"success": False, "message": "Missing required parameters"})

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE seat 
            SET state = 0 
            WHERE schedule_id = %s AND row_num = %s AND col_num = %s AND state = 2
        """, (schedule_id, row_num, col_num))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Seat released successfully"})

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        print(f"Release seat error: {e}")
        return jsonify({"success": False, "message": f"Release seat failed: {str(e)}"})