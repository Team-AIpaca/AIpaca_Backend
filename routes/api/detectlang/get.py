# routes/api/detectlang/get.py
import sys
import json
import fasttext
import os
import re
import datetime
import urllib.parse  # URL 인코딩된 문자열을 디코딩하기 위해 추가

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

def load_model():
    # 현재 스크립트 파일의 절대 경로를 얻음
    dir_path = os.path.dirname(os.path.abspath(__file__))
    
    # 모델 파일 경로 구성
    bin_model_path = os.path.join(dir_path, 'lid.176.bin')
    ftz_model_path = os.path.join(dir_path, 'lid.176.ftz')
    
    if os.path.exists(bin_model_path):
        model = fasttext.load_model(bin_model_path)
    elif os.path.exists(ftz_model_path):
        model = fasttext.load_model(ftz_model_path)
    else:
        model = None
    return model

def sanitize_input(sentence):
    return re.sub(r'[<>\"\'%;()&+]', '', sentence).strip()

def detect_language(sentence, model):
    if not model:
        return create_response_data(5100, "Language detection model file not found."), 500
    
    try:
        sanitized_sentence = sanitize_input(sentence)
        predictions = model.predict(sanitized_sentence)
        # 언어 코드에서 "__label__" 접두어 제거
        language_code = predictions[0][0].replace("__label__", "")
        return create_response_data(200, "Success to get language code!", language_code), 200
    except Exception as e:
        return create_response_data(5009, "Unknown Server Error: " + str(e)), 500

# 결과 데이터 구성 및 출력을 담당하는 함수
def get_response(request_params):
    # 필수 필드 'text'
    required_fields = ['text']
    # 받은 요청 데이터의 키들
    request_keys = request_params.keys()

    # 누락된 필드 찾기
    missing_fields = [field for field in required_fields if field not in request_keys]
    # 알 수 없는 파라미터 찾기
    unknown_params = [key for key in request_keys if key not in required_fields]

    # 필수 필드 누락 또는 알 수 없는 파라미터가 있는 경우
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

    model = load_model()
    # 여기서 text 값을 URL 쿼리 파라미터에서 가져온 후, URL 디코딩 적용
    text = urllib.parse.unquote(request_params['text']) 

    if not model:
        return create_response_data(5100, "Language detection model file not found."), 500

    response_data, status_code = detect_language(text, model)
    return response_data, status_code
