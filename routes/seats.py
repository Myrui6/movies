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
                'state': seat[2]  # 确保返回正确的状态：0=可选，1=已售，2=锁定
            })

        return jsonify({"success": True, "data": seat_list})

    except Exception as e:
        print(f"获取座位错误: {e}")
        return jsonify({"success": False, "message": f"获取座位失败: {str(e)}"})


# 在 seats.py 中添加以下函数
@seats_bp.route('/api/seats/lock', methods=['POST'])
def lock_seat():
    try:
        data = request.get_json()
        schedule_id = data.get('schedule_id')
        row_num = data.get('row')
        col_num = data.get('col')

        if not all([schedule_id, row_num, col_num]):
            return jsonify({"success": False, "message": "缺少必要参数"})

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查座位是否可用（state=0）
        cursor.execute("""
            SELECT state FROM seat 
            WHERE schedule_id = %s AND row_num = %s AND col_num = %s
            FOR UPDATE
        """, (schedule_id, row_num, col_num))

        seat = cursor.fetchone()

        if not seat:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "座位不存在"})

        if seat[0] != 0:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "座位不可用"})

        # 锁定座位（state=2）
        cursor.execute("""
            UPDATE seat 
            SET state = 2 
            WHERE schedule_id = %s AND row_num = %s AND col_num = %s
        """, (schedule_id, row_num, col_num))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "座位锁定成功"})

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        print(f"锁定座位错误: {e}")
        return jsonify({"success": False, "message": f"锁定座位失败: {str(e)}"})

@seats_bp.route('/api/seats/release', methods=['POST'])
def release_seat():
    try:
        data = request.get_json()
        schedule_id = data.get('schedule_id')
        row_num = data.get('row')
        col_num = data.get('col')

        if not all([schedule_id, row_num, col_num]):
            return jsonify({"success": False, "message": "缺少必要参数"})

        conn = get_db_connection()
        cursor = conn.cursor()

        # 只释放锁定状态（state=2）的座位
        cursor.execute("""
            UPDATE seat 
            SET state = 0 
            WHERE schedule_id = %s AND row_num = %s AND col_num = %s AND state = 2
        """, (schedule_id, row_num, col_num))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "座位释放成功"})

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        print(f"释放座位错误: {e}")
        return jsonify({"success": False, "message": f"释放座位失败: {str(e)}"})