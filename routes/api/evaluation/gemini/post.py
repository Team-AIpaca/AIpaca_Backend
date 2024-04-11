# routes/api/evaluation/gemini/post.py

import google.generativeai as genai
import datetime
import requests
from flask import request
import json
import sys
import os

# 현재 파일의 절대 경로를 구합니다.
current_file_path = os.path.abspath(__file__)

# 현재 파일로부터 상위 4개 디렉토리로 이동하여 env_manage.py가 위치한 디렉토리의 경로를 구합니다.
env_manage_directory = os.path.join(current_file_path, '../../../../')

# 이 경로를 sys.path에 추가합니다.
sys.path.insert(0, env_manage_directory)

# 이제 env_manage.py를 임포트할 수 있습니다.
from env_manage import get_env_variable

def detect_language(text):
    # .env 파일에서 FLASK_RUN_PORT 값을 가져옵니다.
    flask_run_port = get_env_variable('FLASK_RUN_PORT')
    # 요청 URL을 구성합니다.
    url = f"http://localhost:{flask_run_port}/api/detectlang"
    # 요청 본문을 구성합니다.
    payload = {"text": text}
    # 요청을 보냅니다.
    response = requests.post(url, json=payload)
    # 응답 JSON을 파싱하여 언어 코드를 반환합니다.
    return response.json().get('data', {}).get('result')

# UTC 타임존 객체 생성 및 현재 시간을 UTC로 가져오기
def get_current_utc_time():
    utc_timezone = datetime.timezone.utc
    return datetime.datetime.now(utc_timezone).isoformat()

def calculate_max_output_tokens(translated_text, base_ratio=1.5):
    """
    번역된 문장의 길이에 기반하여 max_output_tokens 값을 동적으로 계산합니다.
    
    :param translated_text: 번역된 문장
    :param base_ratio: 번역된 문장의 길이에 곱할 비율 (기본값: 1.5)
    :return: 계산된 max_output_tokens 값
    """
    # 공백을 기준으로 번역된 문장을 토큰화하여 토큰 수를 계산
    translated_tokens = len(translated_text.split())
    # 입력 토큰 수에 비례하는 max_output_tokens 값을 계산
    max_output_tokens = int(translated_tokens * base_ratio)
    
    # 최소 및 최대 제한을 설정하여 극단적인 경우 처리
    max_output_tokens = max(50, min(max_output_tokens, 200))
    
    return max_output_tokens

def post_response(request_data):
    # 기본 응답 데이터 구조 설정
    response_data = {
        "StatusCode": 200,
        "message": "Success to request to Gemini!",
        "data": {
            "RequestTime": get_current_utc_time()
        }
    }

    data = request_data
    required_fields = ['GeminiAPIKey', 'Original', 'OriginalLang', 'Translated', 'TranslatedLang', 'EvaluationLang']
    missing_fields = [field for field in required_fields if field not in data]
    unknown_params = [field for field in data if field not in required_fields]

    # GeminiAPIKey가 비어 있는지 확인
    if not data['GeminiAPIKey'].strip():
        response_data["StatusCode"] = 4201
        response_data["message"] = "GeminiAPIKey is required and cannot be empty."
        return response_data, 400

    if missing_fields or unknown_params:
        response_data["StatusCode"] = 4002 if missing_fields else 4003
        response_data["message"] = "Missing fields" if missing_fields else "Unknown parameters"
        if missing_fields:
            response_data["data"]["MissingFields"] = ", ".join(missing_fields)
        if unknown_params:
            response_data["data"]["UnknownParams"] = ", ".join(unknown_params)
        return response_data, 400

    try:
        GOOGLE_API_KEY = data['GeminiAPIKey']
        genai.configure(api_key=GOOGLE_API_KEY)

        # Set up the model
        generation_config = {
        "temperature": 0.4,
        "top_p": 0.8,
        "top_k": 45,
        "max_output_tokens": calculate_max_output_tokens(data['TranslatedLang']),
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
        ]

        model = genai.GenerativeModel('gemini-1.5-pro-latest', generation_config=generation_config, safety_settings=safety_settings)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        instruct_prompt_path = os.path.join(script_dir, '..', 'prompt', 'Instruct_Prompt.md')

        with open(instruct_prompt_path, 'r', encoding='utf-8') as file:
            instruct_prompt_content = file.read()

        combined_text = f"{data['Original']} {data['OriginalLang']} {data['Translated']} {data['TranslatedLang']} {data['EvaluationLang']} {instruct_prompt_content}"
        response = model.generate_content(combined_text)
        raw_text = response.candidates[0].content.parts[0].text
        temp_result_data = raw_text.strip('```json\n').rstrip('```')

        # JSON 문자열을 JSON 객체로 변환
        result_json = json.loads(temp_result_data)

        # print(result_json)

        try:
            # 성공 시 결과 데이터 추가
            response_data["data"]["result"] = result_json
            return response_data, 200
        except:
            response_data["StatusCode"] = 500
            response_data["message"] = "Unknown Error"
            return response_data, 500

    except Exception as e:
        if 'API key not valid' in str(e):
            response_data["StatusCode"] = 4200
            response_data["message"] = "Invalid API Key. Please check API Key."
            return response_data, 400

    return response_data, 200
