# routes/api/user/signup/post.py

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
    return {
        "StatusCode": status_code,
        "message": message,
        "data": data
    }, status_code

def post_response(request_data):
    """사용자 등록 요청 처리 함수"""
    # 필수 필드 검증
    required_fields = ['email', 'password', 'username']
    missing_fields = [field for field in required_fields if field not in request_data]
    unknown_params = [field for field in request_data if field not in required_fields]

    if missing_fields or unknown_params:
        message = ""
        data = {"RequestTime": get_current_utc_time()}
        if missing_fields:
            message += "Missing fields: " + ", ".join(missing_fields) + ". "
            data["MissingFields"] = missing_fields
        if unknown_params:
            message += "Unknown parameters: " + ", ".join(unknown_params) + "."
            data["UnknownParams"] = unknown_params
        return response_structure(400, message.strip(), data)

    # IP 주소 및 User-Agent 검사
    ip_address = request.remote_addr
    user_agent = request.user_agent.string
    if not ip_address or not user_agent:
        message = "Missing IP address or User-Agent."
        data = {
            "RequestTime": get_current_utc_time(),
            "IPAddress": "Present" if ip_address else "Absent",
            "UserAgent": "Present" if user_agent else "Absent"
        }
        return response_structure(400, message, data)

    # 데이터베이스 연결 및 사용자 등록 처리
    try:
        conn = pymysql.connect(**db_config)
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 중복된 유저명 또는 이메일 검사
            cursor.execute("SELECT username, email FROM users WHERE username = %s OR email = %s", 
                           (request_data['username'], request_data['email']))
            if cursor.fetchone():
                return response_structure(400, "Duplicate username or email.", {"RequestTime": get_current_utc_time()
                })

            # 비밀번호 해싱
            hashed_password = bcrypt.hashpw(request_data['password'].encode('utf-8'), bcrypt.gensalt())

            # 사용자 정보를 데이터베이스에 저장
            insert_query = """
            INSERT INTO users (username, email, password, is_active, join_date, join_ip, join_user_agent, password_changed_at, is_email_verified)
            VALUES (%s, %s, %s, 0, NOW(), %s, %s, NOW(), 0)
            """
            cursor.execute(insert_query, (request_data['username'], request_data['email'], hashed_password, ip_address, user_agent))
            conn.commit()  # 변경사항을 데이터베이스에 반영

    except pymysql.MySQLError as err:
        # 데이터베이스 접근 중 오류 발생 시, 상세 오류 메시지와 함께 응답
        return response_structure(500, f"Database error: {err}", {"RequestTime": get_current_utc_time()})
    finally:
        if conn:
            conn.close()  # 사용이 끝난 데이터베이스 연결 종료

    # 사용자 등록 성공 메시지와 함께 응답 데이터 반환
    return response_structure(201, "User registered successfully.", {"RequestTime": get_current_utc_time()})
