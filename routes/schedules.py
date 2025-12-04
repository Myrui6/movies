from flask import Blueprint, request, jsonify
from database import get_db_connection
from datetime import datetime
schedules_bp = Blueprint('schedules', __name__)


@schedules_bp.route('/api/schedules/<int:schedule_id>', methods=['GET'])
def get_schedule_detail(schedule_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 核心修改：使用JOIN查询获取movie_name, hall_name，以及座位信息（从hall表获取）
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
            return jsonify({"success": False, "message": "场次不存在"})

        # 索引根据查询结果调整：start_time(0), price(1), movie_name(2), hall_name(3), total_rows(4), total_columns(5)
        schedule_dict = {
            'start_time': schedule[0].strftime('%Y-%m-%d %H:%M:%S') if schedule[0] else '',
            'price': float(schedule[1]) if schedule[1] else 0,
            'movie_name': schedule[2],
            'hall': schedule[3],  # hall_name
            'seat_rows': schedule[4],  # total_rows
            'seat_columns': schedule[5]  # total_columns
        }

        return jsonify({"success": True, "data": schedule_dict})

    except Exception as e:
        print(f"获取场次详情错误: {e}")
        return jsonify({"success": False, "message": f"获取场次失败: {str(e)}"})


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
    # DELETE 逻辑不变
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM seat WHERE schedule_id = %s", (schedule_id,))
        deleted_seats_count = cursor.fetchone()[0]

        cursor.execute("DELETE FROM schedule WHERE id = %s", (schedule_id,))

        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"success": False, "message": "场次不存在"})

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": f"场次删除成功！共清理 {deleted_seats_count} 个座位和相关订单记录。"})

    except Exception as e:
        conn.rollback()
        print(f"删除场次错误: {e}")
        return jsonify({"success": False, "message": f"删除场次失败: {str(e)}"})


@schedules_bp.route('/api/schedules', methods=['POST'])
def add_schedule():
    data = request.get_json()
    movie_id = data.get('movie_id')
    # 核心修改：接收 hall_id 代替 hall_name, seat_rows, seat_columns
    hall_id = data.get('hall_id')
    start_time = data.get('start_time')
    price = data.get('price')

    if not all([movie_id, hall_id, start_time, price]):
        return jsonify({"success": False, "message": "请填写所有必填字段"})

    # 转换数据类型
    try:
        movie_id = int(movie_id)
        hall_id = int(hall_id)
        price = float(price)
    except ValueError:
        return jsonify({"success": False, "message": "电影ID、影厅ID和价格必须是有效数字"})

    conn = get_db_connection()
    cursor = conn.cursor()
    schedule_id = None
    seat_data = []

    try:
        # 1. 检查影厅是否存在并获取其行数和列数 (从hall表获取座位信息)
        cursor.execute("SELECT name, total_rows, total_columns FROM hall WHERE id = %s", (hall_id,))
        hall_info = cursor.fetchone()

        if not hall_info:
            return jsonify({"success": False, "message": f"影厅ID '{hall_id}' 不存在"})

        seat_rows = hall_info[1]
        seat_columns = hall_info[2]

        # 2. 插入场次信息
        # 核心修改：只插入 movie_id, hall_id, start_time, price
        cursor.execute("""
                       INSERT INTO schedule (movie_id, hall_id, start_time, price)
                       VALUES (%s, %s, %s, %s)
                       """, (movie_id, hall_id, start_time, price))

        # 获取刚插入的场次ID
        schedule_id = cursor.lastrowid

        # 3. 创建座位数据（基于 hall.total_rows 和 hall.total_columns）
        for row in range(1, seat_rows + 1):
            for col in range(1, seat_columns + 1):
                seat_data.append((schedule_id, row, col, 0))  # state=0 表示空闲

        # 批量插入座位数据
        if seat_data:
            cursor.executemany("""
                               INSERT INTO seat (schedule_id, row_num, col_num, state)
                               VALUES (%s, %s, %s, %s)
                               """, seat_data)

        conn.commit()
        return jsonify({"success": True, "message": f"场次添加成功！已自动生成 {len(seat_data)} 个座位。"})

    except Exception as e:
        conn.rollback()
        print(f"添加场次错误: {e}")
        return jsonify({"success": False, "message": f"添加失败: {str(e)}"})
    finally:
        cursor.close()
        conn.close()


@schedules_bp.route('/api/schedules', methods=['GET'])
def get_all_schedules():
    # ... (保持不变，或根据需要更新 JOIN 逻辑) ...
    # 检查您最新的 schedules.py 发现这个函数未提供，但通常是需要的。
    # 假设它是用来获取所有场次的，如果需要，请提供其原代码。
    # 如果它只在内部使用，请忽略此提示。
    return jsonify({"success": False, "message": "此API未实现或未启用"})


@schedules_bp.route('/api/schedules/movie/<int:movie_id>', methods=['GET'])
def get_schedules_by_movie(movie_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 核心修改：使用 JOIN 获取 movie_name 和 hall_name
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
                'hall': sch[4]  # 确保这里返回的是 hall_name
            })

        return jsonify({"success": True, "data": schedule_list})

    except Exception as e:
        print(f"获取影片场次错误: {e}")
        return jsonify({"success": False, "message": f"获取场次失败: {str(e)}"})