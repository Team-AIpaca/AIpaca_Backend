# routes/api/trans/googletrans/get.py

from googletrans import Translator, LANGUAGES
from urllib.parse import unquote
import datetime
import json  # JSON 처리를 위해 추가

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
    required_fields = ['text', 'OriginalLang', "TranslatedLang"]
    request_keys = request_data.keys()

    missing_fields = [field for field in required_fields if field not in request_keys]
    unknown_params = [key for key in request_keys if key not in required_fields]

    if missing_fields or unknown_params:
        message = "Unknown parameters"
        if missing_fields:
            message = "Missing fields"
        if missing_fields and unknown_params:
            message = "Missing fields and Unknown parameters"
        
        # 에러 응답 시 error_info로 MissingFields와 UnknownParams 추가
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

    # Translator 객체 생성
    translator = Translator()

    # 언어 코드가 googletrans에서 사용하는 코드와 일치하는지 확인
    original_lang = original_lang.lower()
    translated_lang = translated_lang.lower()

    # 언어 코드 유효성 검사
    if original_lang not in LANGUAGES or translated_lang not in LANGUAGES:
        return create_response_data(
            4004,
            "Invalid language code",
            error_info={
                "InvalidLangs": ", ".join(filter(lambda x: x not in LANGUAGES, [original_lang, translated_lang]))
            }
        ), 400
    
    # 사용자 입력 텍스트를 URL의 일부로 사용하기 전에 이스케이프 처리된 문자열 복원
    text = unquote(text)

    # 텍스트 번역
    translated_text = translator.translate(text, src=original_lang, dest=translated_lang).text

    # 정상 응답 시 result에 Translation 추가
    return create_response_data(200, "Translation successful", {"Translation": translated_text}), 200
