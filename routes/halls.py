from flask import Blueprint, request, jsonify
from database import get_db_connection

halls_bp = Blueprint('halls', __name__)

@halls_bp.route('/api/halls', methods=['GET'])
def get_halls():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

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
        print(f"Get hall list error: {e}")
        return jsonify({"success": False, "message": f"Get hall failed: {str(e)}"})

@halls_bp.route('/api/halls', methods=['POST'])
def add_hall():
    data = request.get_json()
    name = data.get('name')
    total_rows = data.get('total_rows')
    total_columns = data.get('total_columns')

    if not all([name, total_rows, total_columns]):
        return jsonify({"success": False, "message": "Please fill all required fields"})

    try:
        total_rows = int(total_rows)
        total_columns = int(total_columns)
        if total_rows <= 0 or total_columns <= 0:
            return jsonify({"success": False, "message": "Rows and columns must be positive integers"})

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                           INSERT INTO hall (name, total_rows, total_columns)
                           VALUES (%s, %s, %s)
                           """, (name, total_rows, total_columns))
            conn.commit()

            cursor.close()
            conn.close()

            return jsonify({"success": True, "message": "Hall added successfully!"})
        except Exception as db_e:
            conn.rollback()
            if 'Duplicate entry' in str(db_e) and 'name' in str(db_e):
                return jsonify({"success": False, "message": f"Hall name '{name}' already exists"})
            raise db_e

    except ValueError:
        return jsonify({"success": False, "message": "Rows and columns must be valid numbers"})
    except Exception as e:
        print(f"Add hall error: {e}")
        return jsonify({"success": False, "message": f"Add hall failed: {str(e)}"})

@halls_bp.route('/api/halls/<int:hall_id>', methods=['DELETE'])
def delete_hall(hall_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM schedule WHERE hall_id = %s", (hall_id,))
        schedule_count = cursor.fetchone()[0]

        if schedule_count > 0:
            cursor.close()
            conn.close()
            return jsonify(
                {"success": False, "message": f"Delete failed: This hall has {schedule_count} scheduled screenings, please delete related schedules first."})

        cursor.execute("DELETE FROM hall WHERE id = %s", (hall_id,))
        deleted_rows = cursor.rowcount

        conn.commit()
        cursor.close()
        conn.close()

        if deleted_rows == 0:
            return jsonify({"success": False, "message": "Hall does not exist or has been deleted"})

        return jsonify({"success": True, "message": "Hall deleted successfully!"})

    except Exception as e:
        conn.rollback()
        print(f"Delete hall error: {e}")
        return jsonify({"success": False, "message": f"Delete hall failed: {str(e)}"})