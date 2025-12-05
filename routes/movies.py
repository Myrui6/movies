from flask import Blueprint, request, jsonify
from database import get_db_connection
import base64

movies_bp = Blueprint('movies', __name__)

@movies_bp.route('/api/movies', methods=['POST'])
def add_movie():
    try:
        name = request.form.get('name')
        movie_type = request.form.get('type')
        region = request.form.get('region')
        time = request.form.get('time')
        brief = request.form.get('brief')
        picture = request.files.get('picture')

        if not all([name, movie_type, region, time, brief]):
            return jsonify({"success": False, "message": "Please fill all required fields"})

        picture_data = None
        if picture:
            picture_data = picture.read()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
                       INSERT INTO movie (name, picture, type, region, time, brief)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       """, (name, picture_data, movie_type, region, time, brief))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Movie added successfully"})

    except Exception as e:
        print(f"Add movie error: {e}")
        return jsonify({"success": False, "message": f"Add failed: {str(e)}"})

@movies_bp.route('/api/movies', methods=['GET'])
def get_movies():
    try:
        search_keyword = request.args.get('search', '')
        conn = get_db_connection()
        cursor = conn.cursor()

        if search_keyword:
            cursor.execute("""
                           SELECT id, name, picture, type, region, time, brief
                           FROM movie
                           WHERE name LIKE %s
                              OR type LIKE %s
                              OR region LIKE %s
                              OR brief LIKE %s
                           """,
                           (f'%{search_keyword}%', f'%{search_keyword}%', f'%{search_keyword}%', f'%{search_keyword}%'))
        else:
            cursor.execute("SELECT id, name, picture, type, region, time, brief FROM movie")

        movies = cursor.fetchall()
        cursor.close()
        conn.close()

        movie_list = []
        for movie in movies:
            movie_dict = {
                'id': int(movie[0]),
                'name': str(movie[1]) if movie[1] else '',
                'type': str(movie[3]) if movie[3] else '',
                'region': str(movie[4]) if movie[4] else '',
                'time': int(movie[5]) if movie[5] else 0,
                'brief': str(movie[6]) if movie[6] else '',
                'picture': None
            }

            if movie[2]:
                if isinstance(movie[2], bytes):
                    try:
                        picture_base64 = base64.b64encode(movie[2]).decode('utf-8')
                        movie_dict['picture'] = f"data:image/jpeg;base64,{picture_base64}"
                    except Exception as e:
                        print(f"Convert picture to base64 failed: {e}")
                        movie_dict['picture'] = None
                else:
                    picture_str = str(movie[2])
                    if picture_str.startswith('uploads/'):
                        movie_dict['picture'] = f'/{picture_str}'
                    else:
                        movie_dict['picture'] = picture_str

            movie_list.append(movie_dict)

        return jsonify({"success": True, "data": movie_list})

    except Exception as e:
        print(f"Get movie list error: {e}")
        return jsonify({"success": False, "message": f"Get movie list failed: {str(e)}"})

@movies_bp.route('/api/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM schedule WHERE movie_id = %s", (movie_id,))
        schedule_deleted = cursor.rowcount

        cursor.execute("DELETE FROM movie WHERE id = %s", (movie_id,))
        movie_deleted = cursor.rowcount

        conn.commit()
        cursor.close()
        conn.close()

        if movie_deleted > 0:
            return jsonify({
                "success": True,
                "message": f"Movie removed successfully! Also deleted {schedule_deleted} related schedules"
            })
        else:
            return jsonify({"success": False, "message": "Movie does not exist"})

    except Exception as e:
        print(f"Delete movie error: {e}")
        return jsonify({"success": False, "message": f"Remove failed: {str(e)}"})

@movies_bp.route('/api/movies/<int:movie_id>', methods=['GET'])
def get_movie_detail(movie_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, picture, type, region, time, brief FROM movie WHERE id = %s", (movie_id,))
        movie = cursor.fetchone()

        cursor.close()
        conn.close()

        if not movie:
            return jsonify({"success": False, "message": "Movie does not exist"})

        picture_data = None
        if movie[2]:
            if isinstance(movie[2], bytes):
                try:
                    picture_base64 = base64.b64encode(movie[2]).decode('utf-8')
                    picture_data = f"data:image/jpeg;base64,{picture_base64}"
                except Exception:
                    picture_data = None
            else:
                picture_str = str(movie[2])
                if picture_str.startswith('uploads/'):
                    picture_data = f'/{picture_str}'
                else:
                    picture_data = picture_str

        movie_dict = {
            'id': int(movie[0]),
            'name': str(movie[1]) if movie[1] else '',
            'picture': picture_data,
            'type': str(movie[3]) if movie[3] else '',
            'region': str(movie[4]) if movie[4] else '',
            'time': int(movie[5]) if movie[5] else 0,
            'brief': str(movie[6]) if movie[6] else ''
        }

        return jsonify({"success": True, "data": movie_dict})

    except Exception as e:
        print(f"Get movie detail error: {e}")
        return jsonify({"success": False, "message": f"Get movie detail failed: {str(e)}"})

@movies_bp.route('/api/movies/with-schedules', methods=['GET'])
def get_movies_with_schedules():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT DISTINCT m.id, m.name, m.picture, m.type, m.region, m.time, m.brief
                       FROM movie m
                                INNER JOIN schedule s ON m.id = s.movie_id
                       WHERE s.start_time > NOW()
                       """)
        movies = cursor.fetchall()

        cursor.close()
        conn.close()

        movie_list = []
        for movie in movies:
            movie_dict = {
                'id': int(movie[0]),
                'name': str(movie[1]) if movie[1] else '',
                'type': str(movie[3]) if movie[3] else '',
                'region': str(movie[4]) if movie[4] else '',
                'time': int(movie[5]) if movie[5] else 0,
                'brief': str(movie[6]) if movie[6] else '',
                'picture': None
            }

            if movie[2]:
                if isinstance(movie[2], bytes):
                    try:
                        picture_base64 = base64.b64encode(movie[2]).decode('utf-8')
                        movie_dict['picture'] = f"data:image/jpeg;base64,{picture_base64}"
                    except Exception:
                        movie_dict['picture'] = None
                else:
                    picture_str = str(movie[2])
                    if picture_str.startswith('uploads/'):
                        movie_dict['picture'] = f'/{picture_str}'
                    else:
                        movie_dict['picture'] = picture_str

            movie_list.append(movie_dict)

        return jsonify({"success": True, "data": movie_list})

    except Exception as e:
        print(f"Get movies with schedules error: {e}")
        return jsonify({"success": False, "message": f"Get movie list failed: {str(e)}"})