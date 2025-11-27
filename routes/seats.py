from flask import Blueprint, request, jsonify
from database import get_db_connection

seats_bp = Blueprint('seats', __name__)


@seats_bp.route('/api/seats', methods=['GET'])
def get_seats():
    try:
        schedule_id = request.args.get('schedule_id')

        if not schedule_id:
            return jsonify({"success": False, "message": "缺少场次ID"})

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
        print(f"获取座位错误: {e}")
        return jsonify({"success": False, "message": f"获取座位失败: {str(e)}"})