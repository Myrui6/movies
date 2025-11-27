from flask import Blueprint, request, jsonify
from database import get_db_connection

schedules_bp = Blueprint('schedules', __name__)


@schedules_bp.route('/api/schedules/<int:schedule_id>', methods=['GET'])
def get_schedule_detail(schedule_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT movie_name, start_time, hall, price, seat_rows, seat_columns
                       FROM schedule
                       WHERE id = %s
                       """, (schedule_id,))
        schedule = cursor.fetchone()

        cursor.close()
        conn.close()

        if not schedule:
            return jsonify({"success": False, "message": "场次不存在"})

        schedule_dict = {
            'movie_name': schedule[0],
            'start_time': schedule[1].strftime('%Y-%m-%d %H:%M:%S') if schedule[1] else '',
            'hall': schedule[2],
            'price': float(schedule[3]) if schedule[3] else 0,
            'seat_rows': schedule[4],
            'seat_columns': schedule[5]
        }

        return jsonify({"success": True, "data": schedule_dict})

    except Exception as e:
        print(f"获取场次详情错误: {e}")
        return jsonify({"success": False, "message": f"获取场次详情失败: {str(e)}"})


# 其他原有的 schedules 接口保持不变...
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

        # 转换结果为字典列表
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
        print(f"获取场次列表错误: {e}")
        return jsonify({"success": False, "message": f"获取场次列表失败: {str(e)}"})


@schedules_bp.route('/api/schedules/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 先删除该场次的所有座位
        cursor.execute("DELETE FROM seat WHERE schedule_id = %s", (schedule_id,))
        seats_deleted = cursor.rowcount

        # 再删除场次本身
        cursor.execute("DELETE FROM schedule WHERE id = %s", (schedule_id,))
        schedule_deleted = cursor.rowcount

        conn.commit()
        cursor.close()
        conn.close()

        if schedule_deleted > 0:
            return jsonify({
                "success": True,
                "message": f"场次删除成功！同时删除了 {seats_deleted} 个座位"
            })
        else:
            return jsonify({"success": False, "message": "场次不存在"})

    except Exception as e:
        print(f"删除场次错误: {e}")
        return jsonify({"success": False, "message": f"删除失败: {str(e)}"})

@schedules_bp.route('/api/schedules', methods=['POST'])
def add_schedule():
    try:
        data = request.get_json()
        movie_id = data.get('movie_id')
        movie_name = data.get('movie_name')
        start_time = data.get('start_time')
        hall = data.get('hall')
        seat_rows = data.get('seat_rows')
        seat_columns = data.get('seat_columns')
        price = data.get('price')

        print(f"收到场次数据: {data}")

        # 验证必填字段
        if not all([movie_id, start_time, hall, seat_rows, seat_columns, price]):
            return jsonify({"success": False, "message": "请填写所有必填字段"})

        # 转换数据类型
        try:
            seat_rows = int(seat_rows)
            seat_columns = int(seat_columns)
            price = float(price)
        except ValueError:
            return jsonify({"success": False, "message": "座位行数、列数和价格必须是有效数字"})

        conn = get_db_connection()
        cursor = conn.cursor()

        # 插入场次信息
        cursor.execute("""
                       INSERT INTO schedule (movie_id, movie_name, start_time, hall, seat_rows, seat_columns, price)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)
                       """, (movie_id, movie_name, start_time, hall, seat_rows, seat_columns, price))

        # 获取刚插入的场次ID
        schedule_id = cursor.lastrowid

        # 创建座位数据
        seat_data = []
        for row in range(1, seat_rows + 1):
            for col in range(1, seat_columns + 1):
                seat_data.append((schedule_id, row, col, 0))  # state=0 表示空闲

        # 批量插入座位数据
        cursor.executemany("""
                           INSERT INTO seat (schedule_id, row_num, col_num, state)
                           VALUES (%s, %s, %s, %s)
                           """, seat_data)

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": f"场次添加成功！创建了 {len(seat_data)} 个座位"})

    except Exception as e:
        print(f"添加场次错误: {e}")
        return jsonify({"success": False, "message": f"添加失败: {str(e)}"})