# routes/api/challenge/achieve/post.py

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
        connection = pymysql.connect(cursorclass=pymysql.cursors.DictCursor, **db_config)
        with connection.cursor() as cursor:
            # 파라미터 바인딩을 사용하여 SQL 인젝션 방지
            sql = "SELECT user_id FROM users WHERE username = %s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            return result['user_id'] if result else None
    except Exception as e:
        return None
    finally:
        # 데이터베이스 연결 종료
        connection.close()

def add_achievement_record(user_id, achievement_id):
    """
    사용자의 업적 달성 기록을 데이터베이스에 추가합니다.
    이미 기록이 있는 경우, 기록의 날짜와 함께 실패 메시지를 반환합니다.
    """
    try:
        connection = pymysql.connect(cursorclass=pymysql.cursors.DictCursor, **db_config)
        with connection.cursor() as cursor:
            # 중복 기록 확인
            check_sql = "SELECT achievement_date FROM achievements WHERE user_id = %s AND achievement_id = %s"
            cursor.execute(check_sql, (user_id, achievement_id))
            existing_record = cursor.fetchone()
            if existing_record:
                # 중복 기록이 있으면 ISO 8601 형식으로 날짜 변환 후 반환
                achievement_date_str = existing_record['achievement_date'].isoformat()
                return False, achievement_date_str
            
            # 새 업적 기록 추가
            sql = "INSERT INTO achievements (user_id, achievement_id, achievement_date) VALUES (%s, %s, NOW())"
            cursor.execute(sql, (user_id, achievement_id))
            connection.commit()
            return True, None
    except Exception as e:
        return False, None
    finally:
        connection.close()

def post_response(request_data):
    """
    사용자 인증과 업적 기록 요청을 처리합니다.
    요청 데이터에서 필요한 필드를 검증하고, 사용자 인증 후 업적을 기록합니다.
    """
    # 필수 필드 검증
    required_fields = ['username', 'password', 'achievement_id']
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
        
        # 업적 기록 추가
        success, achievement_date = add_achievement_record(user_id, request_data['achievement_id'])
        if success:
            return response_structure(200, "Achievement recorded successfully.")
        else:
            if achievement_date:
                data = {"duplicate": request_data['achievement_id'], "achievement_date": achievement_date}
                return response_structure(409, "Duplicate achievement record.", data)
            else:
                return response_structure(500, "An error occurred while recording the achievement.")
    else:
        return response_structure(401, message)
