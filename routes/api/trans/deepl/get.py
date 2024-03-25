# routes/api/trans/deepl/get.py

import datetime
import json  # JSON 처리를 위해 추가
from urllib.parse import unquote
import deepl  # DeepL 번역을 위해 deepl 라이브러리를 임포트

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
def post_response(request_params):
    required_fields = ['text', 'OriginalLang', "TranslatedLang", "DeepLAPIKey"]
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
    original_lang = request_params['OriginalLang']
    translated_lang = request_params['TranslatedLang']
    deep_l_api_key = request_params['DeepLAPIKey']

    # 사용자 입력 텍스트를 URL의 일부로 사용하기 전에 이스케이프 처리된 문자열 복원
    text = unquote(text)

    # DeepL 번역 API 사용
    translator = deepl.Translator(deep_l_api_key)

    result = translator.translate_text(text, target_lang=translated_lang, source_lang=original_lang)

    # 완성된 응답 데이터 구성
    return create_response_data(200, "Translation successful", {"Translation": result.text}), 200
