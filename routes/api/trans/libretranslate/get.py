# routes/api/trans/libretranslate/get.py
import os
import sys
from urllib.parse import unquote
from libretranslatepy import LibreTranslateAPI
import datetime
import json  # JSON 처리를 위해 추가

# 현재 파일의 절대 경로를 구합니다.
current_file_path = os.path.abspath(__file__)

# 현재 파일로부터 상위 4개 디렉토리로 이동하여 env_manage.py가 위치한 디렉토리의 경로를 구합니다.
env_manage_directory = os.path.join(current_file_path, '../../../../')

# 이 경로를 sys.path에 추가합니다.
sys.path.insert(0, env_manage_directory)

# 이제 env_manage.py를 임포트할 수 있습니다.
from env_manage import get_env_variable

# UTC 타임존 객체 생성 및 현재 시간을 UTC로 가져오기
def get_current_utc_time():
    utc_timezone = datetime.timezone.utc
    return datetime.datetime.now(utc_timezone).isoformat()

# 기본 응답 데이터 구조를 반환하는 함수
def create_response_data(status_code, message, result=None):
    response_data = {
        "StatusCode": status_code,
        "message": message,
        "data": {
            "RequestTime": get_current_utc_time(),
        }
    }
    if result is not None:
        response_data["data"]["result"] = result
    return response_data

# 결과 데이터 구성 및 출력을 담당하는 함수
def get_response(request_params):
    required_fields = ['text', 'OriginalLang', "TranslatedLang"]
    request_keys = request_params.keys()

    missing_fields = [field for field in required_fields if field not in request_keys]
    unknown_params = [key for key in request_keys if key not in required_fields]

    if missing_fields or unknown_params:
        message = "Unknown parameters"
        if missing_fields:
            message = "Missing fields"
        if missing_fields and unknown_params:
            message = "Missing fields and Unknown parameters"
        
        return create_response_data(
            4003, 
            message, 
            {
                "MissingFields": ", ".join(missing_fields) if missing_fields else None,
                "UnknownParams": ", ".join(unknown_params) if unknown_params else None
            }
        ), 400
    
    text = request_params['text']
    OriginalLang = request_params['OriginalLang']
    TranslatedLang = request_params['TranslatedLang']

    # 사용자 입력 텍스트를 URL의 일부로 사용하기 전에 이스케이프 처리된 문자열 복원
    text = unquote(text)

    # .env에서 libretranslate api 주소를 가져옵니다.
    LibreTranslateAPIURL = get_env_variable('LIBRE_TRANSLATE_API')

    lt = LibreTranslateAPI(LibreTranslateAPIURL)

    translation = lt.translate(text, OriginalLang, TranslatedLang).replace("\\n", "\n")

    # 완성된 응답 데이터 구성
    return create_response_data(200, "Translation successful", {"Translation": translation}), 200

