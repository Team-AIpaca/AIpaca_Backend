# routes/api/evaluation/gpt/post.py

import os
import json
import datetime
import requests
from flask import request
from openai import OpenAI
from openai.types.chat import ChatCompletion

# 언어 코드 확인 API 주소
check_lang_code = "https://apis.uiharu.dev/trans/api2.php"

def get_current_utc_time():
    """현재 UTC 시간을 ISO 형식 문자열로 반환합니다."""
    utc_timezone = datetime.timezone.utc
    return datetime.datetime.now(utc_timezone).isoformat()

def process_response_data(data):
    """JSON 객체를 정렬된 이스케이프 처리되지 않은 문자열로 변환합니다."""
    pretty_result = json.dumps(data, ensure_ascii=False, indent=4)
    return pretty_result

def post_response(request_data):
    """
    OpenAI GPT 모델을 사용하여 요청을 처리하고 응답을 반환합니다.
    
    Args:
        request_data (dict): 클라이언트로부터 받은 요청 데이터를 포함하는 딕셔너리입니다.
    
    Returns:
        tuple: 응답 데이터 딕셔너리와 HTTP 상태 코드를 포함하는 튜플입니다.
    """
    # 기본 응답 구조 설정
    response_data = {
        "StatusCode": 200,
        "message": "Success to request to OpenAI!",
        "data": {
            "RequestTime": get_current_utc_time()
        }
    }

    # 필수 필드 목록
    required_fields = ['OpenAIAPIKey', 'Original', 'OriginalLang', 'Translated', 'TranslatedLang', 'EvaluationLang', 'GPTVersion']
    # 누락된 필드 검사
    missing_fields = [field for field in required_fields if field not in request_data]
    # 알 수 없는 매개변수 검사
    unknown_params = [field for field in request_data if field not in required_fields]

    # 필수 API 키 검사
    api_key = request_data.get('OpenAIAPIKey', '').strip()
    if not api_key:
        response_data["StatusCode"] = 4201
        response_data["message"] = "OpenAIAPIKey is required and cannot be empty."
        return response_data, 400
    if not api_key.startswith('sk-'):
        response_data["StatusCode"] = 4202
        response_data["message"] = "Invalid OpenAIAPIKey format. It should start with 'sk-'."
        return response_data, 400

    # 필수 필드 또는 알 수 없는 매개변수가 있을 경우 응답 처리
    if missing_fields or unknown_params:
        response_data["StatusCode"] = 4002 if missing_fields else 4003
        response_data["message"] = "Missing fields" if missing_fields else "Unknown parameters"
        if missing_fields:
            response_data["data"]["MissingFields"] = ", ".join(missing_fields)
        if unknown_params:
            response_data["data"]["UnknownParams"] = ", ".join(unknown_params)
        return response_data, 400

    # 언어 코드 검증
    headers = {'Content-Type': 'application/json'}
    original_lang_check = requests.post(
        check_lang_code,
        json={"transSentence": request_data['Original'], "targetLang": "ko"},
        headers=headers
    )
    translated_lang_check = requests.post(
        check_lang_code,
        json={"transSentence": request_data['Translated'], "targetLang": "ko"},
        headers=headers
    )

    if original_lang_check.status_code == 200 and translated_lang_check.status_code == 200:
        original_lang_result = original_lang_check.json()['detectedLanguage']
        translated_lang_result = translated_lang_check.json()['detectedLanguage']
        
        # 언어 코드 검증 전 데이터 정규화
        normalized_original_lang = request_data['OriginalLang'].strip().lower()
        normalized_translated_lang = request_data['TranslatedLang'].strip().lower()

        # API 호출 결과 정규화
        normalized_original_result = original_lang_result.strip().lower()
        normalized_translated_result = translated_lang_result.strip().lower()

        if normalized_original_result != normalized_original_lang:
            response_data["StatusCode"] = 4005
            response_data["message"] = f"Language mismatch for Original: Expected {normalized_original_lang}, Detected {normalized_original_result}"
            return response_data, 400

        if normalized_translated_result != normalized_translated_lang:
            response_data["StatusCode"] = 4006
            response_data["message"] = f"Language mismatch for Translated: Expected {normalized_translated_lang}, Detected {normalized_translated_result}"
            return response_data, 400

    else:
        response_data["StatusCode"] = 500
        response_data["message"] = "Failed to verify languages with the language detection API."
        return response_data, 500

    try:
        # OpenAI 클라이언트 초기화
        client = OpenAI(api_key=api_key)

        # 인스트럭션 파일 경로 설정
        script_dir = os.path.dirname(os.path.abspath(__file__))
        instruct_prompt_path = os.path.join(script_dir, '..', 'prompt', 'Instruct_Prompt.md')
        # 인스트럭션 파일 읽기
        with open(instruct_prompt_path, 'r', encoding='utf-8') as file:
            instruct_prompt_content = file.read()

        # 요청 데이터를 JSON 형식으로 조합
        combined_text = json.dumps({
            "Original": request_data['Original'],
            "OriginalLang": request_data['OriginalLang'],
            "Translated": request_data['Translated'],
            "TranslatedLang": request_data['TranslatedLang'],
            "EvaluationLang": request_data['EvaluationLang']
        }, ensure_ascii=False)

        # 요청 및 인스트럭션을 조합
        message_content = f"{combined_text}\n{instruct_prompt_content}"

        # OpenAI GPT 모델로 요청 처리
        completion = client.chat.completions.create(
            model=request_data['GPTVersion'],
            messages=[
                {"role": "user", "content": message_content}
            ],
            temperature=0.25,  # 낮은 불확실성
            top_p=0.8  # 높은 다양성
        )

        # 응답 처리 및 변환
        response_text = json.loads(completion.choices[0].message.content)
        json_process = process_response_data(response_text)
        response_data["data"]["result"] = json.loads(json_process)  # JSON 문자열을 다시 딕셔너리로 변환
        return response_data, 200

    except Exception as e:
        error_message = str(e)
        if 'invalid_api_key' in error_message:
            response_data["StatusCode"] = 401
            response_data["message"] = "Invalid API key provided."
        else:
            response_data["StatusCode"] = 500
            response_data["message"] = f"Unknown error occurred: {error_message}"
        return response_data, 500
