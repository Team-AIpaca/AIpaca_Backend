import datetime
import os
import sys

# 환경 변수 관리 모듈 경로 추가 함수
def add_env_manage_to_path():
    # 현재 파일의 절대 경로를 구한 뒤, 상위 디렉토리로 이동하여 env_manage.py가 위치한 디렉토리의 경로를 구합니다.
    current_file_path = os.path.dirname(os.path.abspath(__file__))
    env_manage_directory = os.path.abspath(os.path.join(current_file_path, os.pardir, os.pardir))

    # 이 경로를 sys.path의 시작 부분에 추가합니다.
    sys.path.insert(0, env_manage_directory)

add_env_manage_to_path()

from env_manage import get_env_variable

# 버전 정보를 불러오는 함수
def get_service_version():
    return get_env_variable('SERVICE_VERSION')

# 현재 UTC 시간을 ISO 형식 문자열로 반환하는 함수
def get_current_utc_time_iso():
    return datetime.datetime.utcnow().isoformat()

# 응답 구성 및 반환 함수
def post_response(request_data):
    service_version = get_service_version()
    response_data = {
        "StatusCode": 200,
        "message": f"Successful version information request",
        "data": {
            "RequestTime": get_current_utc_time_iso(),
            "Version": service_version
        }
    }
    return response_data, 200