# routes/api/data/restore/post.py

import datetime
import os
import sys
from dotenv import load_dotenv

# 환경 설정 파일 로드 및 필요 경로 추가
load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from user.login.post import check_user_info
from env_manage import get_env_variable

# UTC 타임존 객체 생성 및 현재 시간을 UTC로 가져오기
def get_current_utc_time():
    utc_timezone = datetime.timezone.utc
    return datetime.datetime.now(utc_timezone).isoformat()

# 도메인 URL 값 로딩
domain = get_env_variable('DOMAIN')

def restore_database(request_data):
    # 필수 필드 검증
    required_fields = ['username', 'password']
    missing_fields = [field for field in required_fields if field not in request_data]
    
    if missing_fields:
        return response_structure(400, "Missing fields: " + ", ".join(missing_fields))
    
    # 사용자 인증
    username = request_data['username']
    is_authenticated, message = check_user_info(username, request_data['password'])
    
    if not is_authenticated:
        return response_structure(401, message)

    # 유효기간 만료된 파일 삭제
    delete_expired_files('../backup_data', 3)

    # 가장 최신의 백업 파일 찾기
    latest_file = find_latest_backup_file('../backup_data', username)
    if not latest_file:
        return response_structure(404, "No valid backup file found.")

    # URL 반환
    full_url = f"{domain}/api/backup_data/{latest_file}"
    return response_structure(200, "Database can be restored from:", {"url": full_url})

def delete_expired_files(directory, days_valid):
    now = datetime.datetime.now()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            creation_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            if (now - creation_time).days > days_valid:
                os.remove(file_path)

def find_latest_backup_file(directory, username):
    backups = []
    for filename in os.listdir(directory):
        if filename.startswith(username) and filename.endswith('.sql'):
            file_path = os.path.join(directory, filename)
            if is_file_within_validity(file_path, 3):
                backups.append((file_path, os.path.getmtime(file_path)))
    if backups:
        # 가장 최근 파일 반환
        latest_file = max(backups, key=lambda x: x[1])[0]
        return os.path.basename(latest_file)
    return None

def is_file_within_validity(file_path, days_valid):
    creation_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
    return (datetime.datetime.now() - creation_time).days <= days_valid

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
