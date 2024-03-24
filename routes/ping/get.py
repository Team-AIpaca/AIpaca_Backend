# routes/ping/get.py
import datetime

# UTC 타임존 객체 생성 및 현재 시간을 UTC로 가져오기
def get_current_utc_time():
    utc_timezone = datetime.timezone.utc
    return datetime.datetime.now(utc_timezone).isoformat()

def post_response(request_params):
    # 응답 데이터와 HTTP 상태 코드를 함께 구성합니다.
    response_data = {
        "StatusCode": 200,
        "message": "GET request processed. Hello, world!",
        "data": {
            "RequestTime": get_current_utc_time()
        }
    }
    
    # 응답 데이터와 함께 상태 코드를 반환합니다.
    return response_data, 200