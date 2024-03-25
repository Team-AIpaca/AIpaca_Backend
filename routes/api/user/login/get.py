# routes/api/user/login/get.py

import datetime

# UTC 타임존 객체 생성 및 현재 시간을 UTC로 가져오기
def get_current_utc_time():
    utc_timezone = datetime.timezone.utc
    return datetime.datetime.now(utc_timezone).isoformat()

# 기본 응답 데이터 구조를 반환하는 함수
def create_response_data(status_code, message):
    response_data = {
        "StatusCode": status_code,
        "message": message,
        "data": {
            "RequestTime": get_current_utc_time(),
        }
    }

# 결과 데이터 구성 및 출력을 담당하는 함수
def get_response(request_params):
    
    # 응답 데이터와 함께 상태 코드를 반환합니다.
    return create_response_data(4001, "Cannot process GET request. Please use POST method."), 400
