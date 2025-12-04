from flask import Blueprint, request, jsonify
from database import get_db_connection

halls_bp = Blueprint('halls', __name__)


# 获取影厅列表
@halls_bp.route('/api/halls', methods=['GET'])
def get_halls():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取所有影厅的 id, name, total_rows, total_columns
        cursor.execute("SELECT id, name, total_rows, total_columns FROM hall ORDER BY id")
        halls_data = cursor.fetchall()

        cursor.close()
        conn.close()

        halls_list = [
            {
                'id': row[0],
                'name': row[1],
                'total_rows': row[2],
                'total_columns': row[3]
            } for row in halls_data
        ]

        return jsonify({"success": True, "data": halls_list})

    except Exception as e:
        print(f"获取影厅列表错误: {e}")
        return jsonify({"success": False, "message": f"获取影厅失败: {str(e)}"})




# 添加新影厅 (行内添加的“确定”按钮触发)
@halls_bp.route('/api/halls', methods=['POST'])
def add_hall():
    data = request.get_json()
    name = data.get('name')
    total_rows = data.get('total_rows')
    total_columns = data.get('total_columns')

    if not all([name, total_rows, total_columns]):
        return jsonify({"success": False, "message": "请填写所有必填字段"})

    try:
        total_rows = int(total_rows)
        total_columns = int(total_columns)
        if total_rows <= 0 or total_columns <= 0:
            return jsonify({"success": False, "message": "行数和列数必须是正整数"})

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查影厅名是否已存在（利用UNIQUE约束）
        try:
            cursor.execute("""
                           INSERT INTO hall (name, total_rows, total_columns)
                           VALUES (%s, %s, %s)
                           """, (name, total_rows, total_columns))
            conn.commit()

            cursor.close()
            conn.close()

            return jsonify({"success": True, "message": "影厅添加成功！"})
        except Exception as db_e:
            conn.rollback()
            if 'Duplicate entry' in str(db_e) and 'name' in str(db_e):
                return jsonify({"success": False, "message": f"影厅名 '{name}' 已存在"})
            raise db_e  # 抛出其他数据库错误

    except ValueError:
        return jsonify({"success": False, "message": "行数和列数必须是有效数字"})
    except Exception as e:
        print(f"添加影厅错误: {e}")
        return jsonify({"success": False, "message": f"添加影厅失败: {str(e)}"})


# 删除影厅
@halls_bp.route('/api/halls/<int:hall_id>', methods=['DELETE'])
def delete_hall(hall_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. 检查是否有排片场次引用该影厅
        cursor.execute("SELECT COUNT(*) FROM schedule WHERE hall_id = %s", (hall_id,))
        schedule_count = cursor.fetchone()[0]

        if schedule_count > 0:
            cursor.close()
            conn.close()
            return jsonify(
                {"success": False, "message": f"删除失败：该影厅下有 {schedule_count} 个排片场次，请先删除相关场次。"})

        # 2. 执行删除操作
        cursor.execute("DELETE FROM hall WHERE id = %s", (hall_id,))
        deleted_rows = cursor.rowcount

        conn.commit()
        cursor.close()
        conn.close()

        if deleted_rows == 0:
            return jsonify({"success": False, "message": "影厅不存在或已被删除"})

        return jsonify({"success": True, "message": "影厅删除成功！"})

    except Exception as e:
        conn.rollback()
        print(f"删除影厅错误: {e}")
        return jsonify({"success": False, "message": f"删除影厅失败: {str(e)}"})