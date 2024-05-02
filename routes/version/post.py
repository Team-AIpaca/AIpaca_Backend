# routes/version/post.py

import datetime
import os
import sys

# 버전 정보를 version.txt 파일에서 불러오는 함수
def get_service_version():
    # version.txt 파일의 경로를 설정합니다.
    current_file_path = os.path.dirname(os.path.abspath(__file__))
    version_file_path = os.path.join(current_file_path, 'version.txt')

    # 파일을 읽어 첫 번째 줄을 반환합니다.
    with open(version_file_path, 'r') as file:
        version = file.readline().strip()  # strip()을 사용하여 줄바꿈을 제거합니다.
    return version

# 현재 UTC 시간을 ISO 형식 문자열로 반환하는 함수
def get_current_utc_time():
    utc_timezone = datetime.timezone.utc
    return datetime.datetime.now(utc_timezone).isoformat()

# 응답 구성 및 반환 함수
def post_response(request_data):
    service_version = get_service_version()
    response_data = {
        "StatusCode": 200,
        "message": "Successful version information request",
        "data": {
            "RequestTime": get_current_utc_time(),
            "Version": service_version
        }
    }
    return response_data, 200

