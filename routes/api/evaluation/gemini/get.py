# routes/api/evaluation/gemini/get.py

import datetime

def get_response():
    # UTC 타임존 객체 생성
    utc_timezone = datetime.timezone.utc

    # 현재 시간을 UTC로 가져오기
    current_time = datetime.datetime.now(utc_timezone).isoformat()

    # 응답 데이터와 HTTP 상태 코드를 함께 구성합니다.
    response_data = {
        "StatusCode": 4001,
        "message": "Cannot process GET request. Please use POST method.",
        "data": {
            "RequestTime": current_time
        }
    }
    
    # 응답 데이터와 함께 상태 코드를 반환합니다.
    return response_data, 400