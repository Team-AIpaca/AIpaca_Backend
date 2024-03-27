# routes/api/detectlang/get.py

import sys
import json
import fasttext
from urllib.parse import unquote
import os
import re
import datetime

def get_current_utc_time():
    """
    현재 UTC 시간을 ISO 8601 형식의 문자열로 반환하는 함수.
    """
    utc_timezone = datetime.timezone.utc
    return datetime.datetime.now(utc_timezone).isoformat()

def create_response_data(status_code, message, result=None):
    """
    API 응답을 위한 데이터 구조를 생성하는 함수.
    입력으로 상태 코드, 메시지, 결과를 받아 응답 데이터를 구성한다.
    
    :param status_code: 응답의 HTTP 상태 코드
    :param message: 클라이언트에 전달할 메시지
    :param result: 요청에 대한 결과 데이터 (선택적)
    :return: 응답 데이터 딕셔너리
    """
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
    """
    언어 감지 모델 파일을 로드하는 함수.
    현재 디렉토리 내에서 미리 정의된 파일명을 가진 모델 파일을 찾아 로드한다.
    
    :return: 로드된 모델, 실패 시 None 반환
    """
    dir_path = os.path.dirname(os.path.abspath(__file__))
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
    """
    입력된 문장에서 잠재적인 SQL 인젝션 공격을 방지하기 위해 특수 문자를 제거하는 함수.
    
    :param sentence: 원본 문장
    :return: 특수 문자가 제거된 문장
    """
    # 여기에서 이스케이프 시퀀스를 올바르게 처리하도록 수정합니다.
    return re.sub(r'[<>\"\'%;()&+]', '', sentence.replace("\\", "\\\\")).strip()

def detect_language(sentence, model):
    """
    주어진 문장의 언어를 감지하는 함수.
    fasttext 모델을 사용하여 언어를 예측하고 결과를 반환한다.
    
    :param sentence: 언어를 감지할 문장
    :param model: 언어 감지를 위해 사용할 fasttext 모델
    :return: 감지된 언어 코드를 포함한 응답 데이터 및 상태 코드
    """
    if not model:
        return create_response_data(5100, "Language detection model file not found."), 500
    
    try:
        sanitized_sentence = sanitize_input(sentence)
        predictions = model.predict(sanitized_sentence)
        language_code = predictions[0][0].replace("__label__", "")
        return create_response_data(200, "Success to get language code!", language_code), 200
    except Exception:
        return create_response_data(5009, "Unknown Server Error"), 500

def post_response(request_data):
    """
    HTTP POST 요청에 대한 응답을 생성하는 함수.
    요청 데이터에서 필요한 정보를 추출
    
    :param request_data: 클라이언트로부터 받은 요청 데이터
    :return: 생성된 응답 데이터 및 상태 코드
    """
    # 필수 필드 'text'를 확인하기 위한 설정
    required_fields = ['text']
    # 요청 데이터에서 제공된 키들을 추출
    request_keys = request_data.keys()

    # 요청에서 누락된 필수 필드를 찾음
    missing_fields = [field for field in required_fields if field not in request_keys]
    # 요청에서 필수 필드가 아닌 추가적인 키를 찾음
    unknown_params = [key for key in request_keys if key not in required_fields]

    # 필수 필드가 누락되었거나 알 수 없는 파라미터가 있는 경우 에러 메시지와 함께 응답
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

    # 모델 로드
    model = load_model()
    
    # 사용자 입력 텍스트를 URL의 일부로 사용하기 전에 이스케이프 처리된 문자열 복원
    text = unquote(text)

    # 요청 데이터에서 'text' 필드 값을 가져옴
    text = request_data['text'].replace("\n", "\\n")

    # 모델이 없는 경우 오류 메시지 반환
    if not model:
        return create_response_data(5100, "Language detection model file not found."), 500

    # 언어 감지 실행 및 결과 반환
    response_data, status_code = detect_language(text, model)
    return response_data, status_code
