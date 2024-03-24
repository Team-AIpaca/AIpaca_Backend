# routes/api/user/login/post.py

import datetime
import os
import sys
from flask import request
import bcrypt
import pymysql
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 데이터베이스 설정 로드
# sys.path.append를 사용하여 상위 디렉토리의 모듈에 접근 가능하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.db_config import db_config

def get_current_utc_time():
    """현재 시간을 UTC 기준으로 가져오는 함수"""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def response_structure(status_code=200, message="", data=None):
    """응답 데이터 구조를 생성하는 함수"""
    if data is None:
        data = {}
    
    data["RequestTime"] = get_current_utc_time()

    return {
        "StatusCode": status_code,
        "message": message,
        "data": data
    }, status_code

def check_user_info(username, password):
    """사용자 정보가 일치하는지 확인하는 함수"""
    try:
        # 데이터베이스 연결
        conn = pymysql.connect(**db_config)
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 사용자 조회
            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            if not user:
                # 사용자가 존재하지 않음
                return False, "User does not exist."

            # 비밀번호 확인
            if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                # 비밀번호가 일치
                return True, "User authenticated successfully."
            else:
                # 비밀번호가 일치하지 않음
                return False, "Duplicate entry found"
    except pymysql.MySQLError as err:
        # 데이터베이스 오류 처리
        return False, f"Database error: {err}"
    finally:
        # 데이터베이스 연결 종료
        if conn:
            conn.close()

def post_response(request_data):
    """사용자 인증 요청 처리 함수"""
    # 필수 필드 검증
    required_fields = ['username', 'password']
    missing_fields = [field for field in required_fields if field not in request_data]

    if missing_fields:
        message = "Missing fields: " + ", ".join(missing_fields) + "."
        data = {"RequestTime": get_current_utc_time(), "MissingFields": missing_fields}
        return response_structure(400, message, data)

    # 사용자 정보 확인
    is_authenticated, message = check_user_info(request_data['username'], request_data['password'])

    if is_authenticated:
        # 인증 성공
        return response_structure(200, "User authenticated successfully.")
    else:
        # 인증 실패
        return response_structure(401, message)