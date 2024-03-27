# routes/api/trans/deepl/post.py

import datetime
import json  # JSON 처리를 위해 추가
import deepl  # DeepL 번역을 위해 deepl 라이브러리를 임포트

# UTC 타임존 객체 생성 및 현재 시간을 UTC로 가져오기
def get_current_utc_time():
    utc_timezone = datetime.timezone.utc
    return datetime.datetime.now(utc_timezone).isoformat()

# 기본 응답 데이터 구조를 반환하는 함수
def create_response_data(status_code, message, result=None, error_info=None):
    response_data = {
        "StatusCode": status_code,
        "message": message,
        "data": {
            "RequestTime": get_current_utc_time(),
        }
    }
    # 정상 응답인 경우 result를 사용해 데이터 구성
    if result is not None:
        response_data["data"]["result"] = result
    # 에러 정보가 있는 경우, 이를 data에 직접 추가
    if error_info is not None:
        response_data["data"].update(error_info)
    return response_data

# 결과 데이터 구성 및 출력을 담당하는 함수
def post_response(request_data):
    required_fields = ['text', 'OriginalLang', "TranslatedLang", "DeepLAPIKey"]
    request_keys = request_data.keys()

    missing_fields = [field for field in required_fields if field not in request_keys]
    unknown_params = [key for key in request_keys if key not in required_fields]

    if missing_fields or unknown_params:
        message = "Unknown parameters"
        if missing_fields:
            message = "Missing fields"
        if missing_fields and unknown_params:
            message = "Missing fields and Unknown parameters"
        
        # 수정: 에러 응답 시 error_info로 MissingFields와 UnknownParams 추가
        return create_response_data(
            4003, 
            message, 
            error_info={
                "MissingFields": ", ".join(missing_fields) if missing_fields else None,
                "UnknownParams": ", ".join(unknown_params) if unknown_params else None
            }
        ), 400
    
    text = request_data['text']
    original_lang = request_data['OriginalLang']
    translated_lang = request_data['TranslatedLang']
    deep_l_api_key = request_data['DeepLAPIKey']

    # DeepL 번역 API 사용
    translator = deepl.Translator(deep_l_api_key)

    result = translator.translate_text(text, target_lang=translated_lang, source_lang=original_lang)

    # 정상 응답 시 result에 Translation 추가
    return create_response_data(200, "Translation successful", {"Translation": result.text}), 200
