from flask import Blueprint, request, jsonify
from database import get_db_connection
import os
import base64
from datetime import datetime

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
            return jsonify({"success": False, "message": "请填写所有必填字段"})

        # 处理图片上传 - 存储为二进制数据
        picture_data = None
        if picture:
            # 读取图片文件为二进制数据
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

        return jsonify({"success": True, "message": "影片添加成功"})

    except Exception as e:
        print(f"添加影片错误: {e}")
        return jsonify({"success": False, "message": f"添加失败: {str(e)}"})


@movies_bp.route('/api/movies', methods=['GET'])
def get_movies():
    try:
        search_keyword = request.args.get('search', '')
        conn = get_db_connection()
        cursor = conn.cursor()

        if search_keyword:
            # 模糊搜索
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
            # 获取所有电影
            cursor.execute("SELECT id, name, picture, type, region, time, brief FROM movie")

        movies = cursor.fetchall()
        cursor.close()
        conn.close()

        # 处理混合格式的图片数据
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

            # 处理图片数据
            if movie[2]:
                if isinstance(movie[2], bytes):
                    # 二进制数据 - 转换为base64
                    try:
                        picture_base64 = base64.b64encode(movie[2]).decode('utf-8')
                        movie_dict['picture'] = f"data:image/jpeg;base64,{picture_base64}"
                    except Exception as e:
                        print(f"转换图片base64失败: {e}")
                        movie_dict['picture'] = None
                else:
                    # 字符串数据 - 可能是文件路径
                    picture_str = str(movie[2])
                    if picture_str.startswith('uploads/'):
                        movie_dict['picture'] = f'/{picture_str}'
                    else:
                        movie_dict['picture'] = picture_str

            movie_list.append(movie_dict)

        return jsonify({"success": True, "data": movie_list})

    except Exception as e:
        print(f"获取电影列表错误: {e}")
        return jsonify({"success": False, "message": f"获取电影列表失败: {str(e)}"})


@movies_bp.route('/api/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 先删除该影片对应的所有场次
        cursor.execute("DELETE FROM schedule WHERE movie_id = %s", (movie_id,))
        schedule_deleted = cursor.rowcount

        # 再删除影片本身
        cursor.execute("DELETE FROM movie WHERE id = %s", (movie_id,))
        movie_deleted = cursor.rowcount

        conn.commit()
        cursor.close()
        conn.close()

        if movie_deleted > 0:
            return jsonify({
                "success": True,
                "message": f"影片下架成功！同时删除了 {schedule_deleted} 个相关场次"
            })
        else:
            return jsonify({"success": False, "message": "影片不存在"})

    except Exception as e:
        print(f"删除影片错误: {e}")
        return jsonify({"success": False, "message": f"下架失败: {str(e)}"})

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
            return jsonify({"success": False, "message": "影片不存在"})

        # 处理图片数据
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
        print(f"获取影片详情错误: {e}")
        return jsonify({"success": False, "message": f"获取影片详情失败: {str(e)}"})


@movies_bp.route('/api/movies/with-schedules', methods=['GET'])
def get_movies_with_schedules():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 查询有场次的影片
        cursor.execute("""
                       SELECT DISTINCT m.id, m.name, m.picture, m.type, m.region, m.time, m.brief
                       FROM movie m
                                INNER JOIN schedule s ON m.id = s.movie_id
                       WHERE s.start_time > NOW()
                       """)
        movies = cursor.fetchall()

        cursor.close()
        conn.close()

        # 处理图片数据
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

            # 处理图片数据
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
        print(f"获取有场次影片错误: {e}")
        return jsonify({"success": False, "message": f"获取影片列表失败: {str(e)}"})