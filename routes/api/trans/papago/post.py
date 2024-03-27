# routes/api/trans/papago/post.py

import datetime  # datetime 모듈을 임포트합니다. 날짜와 시간을 다루는 데 필요합니다.
import json  # JSON 데이터를 처리하기 위한 모듈입니다.
from papygo.translator import Translator  # papygo 라이브러리에서 Translator 클래스를 임포트합니다. 번역 기능을 사용하기 위함입니다.

def get_current_utc_time():
    # 현재 UTC 시간을 ISO 8601 형식의 문자열로 반환하는 함수입니다.
    utc_timezone = datetime.timezone.utc  # UTC 타임존 객체를 생성합니다.
    return datetime.datetime.now(utc_timezone).isoformat()  # 현재 UTC 시간을 ISO 형식의 문자열로 반환합니다.

def create_response_data(status_code, message, result=None, error_info=None):
    # API 응답을 위한 데이터를 생성하는 함수입니다.
    response_data = {
        "StatusCode": status_code,  # 상태 코드 (예: 200, 400, 500)
        "message": message,  # 응답 메시지 (예: "Translation successful")
        "data": {
            "RequestTime": get_current_utc_time(),  # 요청 시간을 UTC로 기록합니다.
        }
    }
    if result is not None:
        response_data["data"]["result"] = result  # 결과 데이터가 있다면 추가합니다.
    if error_info is not None:
        response_data["data"].update(error_info)  # 오류 정보가 있다면 추가합니다.
    return response_data  # 생성된 응답 데이터를 반환합니다.

def post_response(request_data):
    # 요청을 처리하고 응답을 반환하는 함수입니다.
    # 필수 및 선택적 필드를 정의합니다.
    required_fields = ['text', 'OriginalLang', "TranslatedLang", "ClientID", "ClientSecret"]
    optional_fields = ['APIType']
    request_keys = request_data.keys()

    # 필수 필드가 누락되거나 알 수 없는 매개변수가 있는지 확인합니다.
    missing_fields = [field for field in required_fields if field not in request_keys]
    unknown_params = [key for key in request_keys if key not in required_fields + optional_fields]

    # 필수 필드 누락이나 알 수 없는 매개변수가 있을 경우 오류 메시지를 반환합니다.
    if missing_fields or unknown_params:
        message = "Unknown parameters"
        if missing_fields:
            message = "Missing fields"
        if missing_fields and unknown_params:
            message = "Missing fields and Unknown parameters"
        
        return create_response_data(
            4003, 
            message, 
            error_info={
                "MissingFields": ", ".join(missing_fields) if missing_fields else None,
                "UnknownParams": ", ".join(unknown_params) if unknown_params else None
            }
        ), 400

    # 요청 데이터에서 필요한 값을 추출합니다.
    text = request_data['text']
    original_lang = request_data['OriginalLang']
    translated_lang = request_data['TranslatedLang']
    client_id = request_data['ClientID']
    client_secret = request_data['ClientSecret']
    api_type = request_data.get('APIType', 'naver_cloud')  # 기본값으로 'naver_cloud'를 사용합니다.

    # 지원되지 않는 API 유형이 지정되었는지 확인합니다.
    if api_type not in ['naver_cloud', 'naver_cloud_gov']:
        return create_response_data(4004, "Invalid APIType value. Please use 'naver_cloud' or 'naver_cloud_gov'."), 400

    translator = Translator(client_id, client_secret, api_type)  # 번역기 객체를 생성합니다.

    try:
        # 번역을 시도하고 성공 시 결과를 반환합니다.
        result = translator.translate(text, original_lang, translated_lang)
        # 번역 성공 응답을 생성하여 반환합니다.
        return create_response_data(200, "Translation successful", {"Translation": result}), 200
    except Exception as e:
        # 번역 과정에서 예외가 발생한 경우 오류 처리를 수행합니다.
        error_message = str(e)
        if "Unauthorized" in error_message:
            # 클라이언트 ID 또는 시크릿 키가 유효하지 않은 경우의 오류 처리
            return create_response_data(401, "Invalid ClientID or ClientSecret value. Please check them."), 401
        else:
            # 기타 오류 발생 시, 오류 메시지를 포함하여 응답 데이터를 생성하고 반환합니다.
            return create_response_data(5000, "An error occurred during translation", error_info={"Error": error_message}), 500
