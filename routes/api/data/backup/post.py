# routes/api/data/backup/post.py

import datetime
import os
import hashlib
import pymysql
import bcrypt
import sys

# 로그인 정보 가져오기
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from user.login.post import check_user_info

# UTC 타임존 객체 생성 및 현재 시간을 UTC로 가져오기
def get_current_utc_time():
    utc_timezone = datetime.timezone.utc
    return datetime.datetime.now(utc_timezone).isoformat()

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

# SQL 파일 해시를 검증하는 함수
def validate_file_hash(sql_file, received_hash):
    """SQL 파일의 해시를 검증합니다."""
    actual_hash = hashlib.sha256(sql_file.encode('utf-8')).hexdigest()
    return received_hash == actual_hash

# 파일을 안전하게 저장하는 함수
def save_backup_file(username, sql_file, backup_folder='../backup_data'):
    """SQL 파일을 안전하게 백업 디렉토리에 저장합니다. 기존 유저 파일은 삭제합니다."""
    if not os.access(backup_folder, os.W_OK):
        os.makedirs(backup_folder, exist_ok=True)

    # 기존 파일 삭제
    for file in os.listdir(backup_folder):
        if file.startswith(username + "_"):
            os.remove(os.path.join(backup_folder, file))
    
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{username}_{current_time}.sql"
    file_path = os.path.join(backup_folder, filename)
    
    with open(file_path, 'w') as file:
        file.write(sql_file)
    
    return file_path

# POST 요청을 처리하는 함수
def post_response(request_data):

    # 필수 필드 검증
    required_fields = ['username', 'password', 'sql_file', 'sql_hash']
    missing_fields = [field for field in required_fields if field not in request_data]

    if missing_fields:
        message = "Missing fields: " + ", ".join(missing_fields) + "."
        data = {"MissingFields": missing_fields}
        return response_structure(400, message, data)

    # 사용자 정보 확인
    username = request_data['username']
    is_authenticated, message = check_user_info(username, request_data['password'])

    if not is_authenticated:
        # 로그인 정보 불일치
        return response_structure(401, message)

    # 파일 해시 확인
    sql_file = request_data.get('sql_file')
    received_hash = request_data.get('sql_hash')

    if not validate_file_hash(sql_file, received_hash):
        message = "File hash does not match."
        return response_structure(400, message)

    # 백업 파일 저장
    try {
        file_path = save_backup_file(username, sql_file)
        message = "Backup successful."
        return response_structure(200, message)
    except IOError as e:
        message = f"Failed to write file: {str(e)}"
        return response_structure(500, message)
