# routes/api/trans/googletrans/post.py
from googletrans import Translator, LANGUAGES
import datetime
import json  # JSON 처리를 위해 추가

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
        
        return create_response_data(
            4003, 
            message, 
            {
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
            {"InvalidLangs": ", ".join(filter(lambda x: x not in LANGUAGES, [original_lang, translated_lang]))}
        ), 400

    # 텍스트 번역
    translated_text = translator.translate(text, src=original_lang, dest=translated_lang).text

    # 완성된 응답 데이터 구성
    return create_response_data(200, "Translation successful", {"Translation": translated_text}), 200
