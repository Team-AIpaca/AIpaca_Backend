# routes/api/challenge/verify/post.py

import datetime
import os
import sys
import pymysql
from dotenv import load_dotenv

load_dotenv()

current_file_path = os.path.abspath(__file__)
db_config_path = os.path.dirname(os.path.dirname(current_file_path))
sys.path.append(db_config_path)
from db.db_config import db_config  # 환경변수를 통한 DB 설정 로드

check_user_info_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_file_path))), 'user', 'login')
sys.path.append(check_user_info_path)
from post import check_user_info  # 안전한 비밀번호 확인 로직 사용 가정

def get_current_utc_time():
    """UTC 현재 시간을 ISO 8601 문자열로 반환합니다."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def response_structure(status_code=200, message="", data=None):
    """API 응답 구조를 생성합니다."""
    response_data = {"RequestTime": get_current_utc_time()}
    if data is not None:
        response_data.update(data)
    return {"StatusCode": status_code, "message": message, "data": response_data}, status_code

def get_user_id(username):
    """사용자 ID를 데이터베이스에서 조회합니다."""
    try:
        # 안전한 연결: db_config는 외부 환경 변수에서 로드된 설정
        connection = pymysql.connect(cursorclass=pymysql.cursors.DictCursor, **db_config)
        with connection.cursor() as cursor:
            # 안전한 SQL 쿼리: 파라미터 바인딩을 사용하여 SQL 인젝션 방지
            sql = "SELECT user_id FROM users WHERE username = %s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            return result['user_id'] if result else None
    except Exception as e:
        return None
    finally:
        # 데이터베이스 연결 종료
        connection.close()

def get_achievement_records(user_id):
    """
    사용자 ID를 기반으로 모든 업적 기록을 조회하고,
    datetime 객체를 ISO 8601 포맷 문자열로 변환합니다.
    """
    try:
        connection = pymysql.connect(cursorclass=pymysql.cursors.DictCursor, **db_config)
        with connection.cursor() as cursor:
            sql = "SELECT achievement_id, achievement_date FROM achievements WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
            achievements_raw = cursor.fetchall()
            
            # datetime 객체를 ISO 8601 포맷 문자열로 변환
            achievements = [{'achievement_id': ach['achievement_id'], 'achievement_date': ach['achievement_date'].isoformat()} for ach in achievements_raw]
            return achievements
    except Exception as e:
        return None
    finally:
        connection.close()

def post_response(request_data):
    """
    사용자 인증 후 해당 사용자가 달성한 모든 업적 목록과 달성 날짜를 반환합니다.
    """
    # 필수 필드 검증: 이제 'achievement_id'는 필요하지 않음
    required_fields = ['username', 'password']
    missing_fields = [field for field in required_fields if field not in request_data]
    if missing_fields:
        message = "Missing fields: " + ", ".join(missing_fields) + "."
        data = {"MissingFields": missing_fields}
        return response_structure(400, message, data)
    
    # 사용자 인증
    is_authenticated, message = check_user_info(request_data['username'], request_data['password'])
    if is_authenticated:
        user_id = get_user_id(request_data['username'])
        if user_id is None:
            return response_structure(404, "User not found.")
        
        # 사용자 업적 기록 조회
        achievements = get_achievement_records(user_id)
        if achievements is not None:
            data = {"achievements": achievements}
            return response_structure(200, "User achievements retrieved successfully.", data)
        else:
            return response_structure(500, "An error occurred while retrieving achievements.")
    else:
        return response_structure(401, message)