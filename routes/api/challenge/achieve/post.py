# routes/api/challenge/achieve/post.py

import datetime
import os
import sys
import json
import pymysql
import pytz
from dotenv import load_dotenv

load_dotenv()

current_file_path = os.path.abspath(__file__)
db_config_path = os.path.dirname(os.path.dirname(current_file_path))
sys.path.append(db_config_path)
from db.db_config import db_config  # 환경변수를 통한 DB 설정 로드

check_user_info_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_file_path))), 'user', 'login')
sys.path.append(check_user_info_path)
from post import check_user_info

env_manage_directory = os.path.join(current_file_path, '../../../../')
sys.path.insert(0, env_manage_directory)
from env_manage import get_env_variable

timezone = get_env_variable('TIMEZONE')

def get_current_time():
    """환경 변수에서 설정된 시간대를 기준으로 현재 시간을 반환합니다."""
    try:
        tz = pytz.timezone(timezone)
    except Exception:
        tz = pytz.utc  # 시간대 정보가 올바르지 않거나 없으면 UTC를 사용
    return datetime.datetime.now(tz)

def get_achievement_info():
    """list.json에서 도전과제 정보를 읽어 반환합니다. 파일이 없으면 오류를 반환합니다."""
    achievements_file_path = os.path.join(os.path.dirname(current_file_path), 'list.json')
    # 파일의 존재 여부를 확인
    if not os.path.exists(achievements_file_path):
        return False, "Achievement list file not found."
    try:
        with open(achievements_file_path, 'r') as file:
            return True, json.load(file)
    except json.JSONDecodeError:
        # JSON 형식이 잘못된 경우
        return False, "Invalid JSON format in the achievement list file."

def validate_achievement(achievement_id):
    """도전과제 ID의 유효성을 검증합니다."""
    success, achievements = get_achievement_info()
    if not success:
        # 오류 메시지를 반환하는 경우
        return False, achievements  # achievements 변수에는 이 경우 오류 메시지가 담겨있습니다.
    
    achievement = achievements.get(achievement_id, None)
    if not achievement:
        return False, "Achievement ID does not exist."

    if achievement['is_available'] != "yes":
        return False, "Achievement is not available."

    current_time = get_current_time()
    start_time = datetime.datetime.strptime(str(achievement['start_date']), "%Y%m%d%H%M%S").replace(tzinfo=pytz.utc)
    end_time = None

    if achievement['end_date']:
        end_time = datetime.datetime.strptime(str(achievement['end_date']), "%Y%m%d%H%M%S").replace(tzinfo=pytz.utc)

    if current_time < start_time:
        return False, "Achievement start date has not been reached."
    
    if end_time and current_time > end_time:
        return False, "Achievement end date has passed."

    return True, None

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
    요청 데이터에서 필요한 필드를 검증하고, 도전과제의 유효성을 검사한 후,
    사용자 인증을 수행하고 업적을 기록합니다.
    """
    # 필수 필드 검증
    required_fields = ['username', 'password', 'achievement_id']
    missing_fields = [field for field in required_fields if field not in request_data]
    if missing_fields:
        # 필수 필드가 누락된 경우 400 상태 코드와 함께 메시지 반환
        message = "Missing fields: " + ", ".join(missing_fields) + "."
        data = {"MissingFields": missing_fields}
        return response_structure(400, message, data)
    
    # 도전과제 유효성 검증
    valid_achievement, message = validate_achievement(request_data['achievement_id'])
    if not valid_achievement:
        # 도전과제가 유효하지 않은 경우 400 상태 코드와 함께 메시지 반환
        return response_structure(400, message)
    
    # 사용자 인증
    is_authenticated, message = check_user_info(request_data['username'], request_data['password'])
    if is_authenticated:
        # 사용자 ID 조회
        user_id = get_user_id(request_data['username'])
        if user_id is None:
            # 사용자 ID가 조회되지 않는 경우 404 상태 코드와 함께 메시지 반환
            return response_structure(404, "User not found.")
        
        # 업적 기록 추가
        success, achievement_date = add_achievement_record(user_id, request_data['achievement_id'])
        if success:
            # 업적 기록 추가 성공 시 200 상태 코드와 함께 성공 메시지 반환
            return response_structure(200, "Achievement recorded successfully.")
        else:
            if achievement_date:
                # 도전과제 기록이 중복되는 경우 409 상태 코드와 함께 메시지 반환
                data = {"duplicate": request_data['achievement_id'], "achievement_date": achievement_date}
                return response_structure(409, "Duplicate achievement record.", data)
            else:
                # 기타 오류 발생 시 500 상태 코드와 함께 메시지 반환
                return response_structure(500, "An error occurred while recording the achievement.")
    else:
        # 사용자 인증 실패 시 401 상태 코드와 함께 메시지 반환
        return response_structure(401, message)