# routes/api/evaluation/gemini/post.py
import google.generativeai as genai
import datetime
import requests
from flask import request
import json
import os

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

def post_response(request_data):
    # 기본 응답 데이터 구조 설정
    response_data = {
        "StatusCode": 200,
        "message": "Success to request to Gemini!",
        "data": {
            "RequestTime": get_current_utc_time()
        }
    }

    data = request.get_json() or request_data
    required_fields = ['GeminiAPIKey', 'Original', 'OriginalLang', 'Translated', 'TranslatedLang', 'EvaluationLang']
    missing_fields = [field for field in required_fields if field not in data]
    unknown_params = [field for field in data if field not in required_fields]

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
        model = genai.GenerativeModel('gemini-pro')
        script_dir = os.path.dirname(os.path.abspath(__file__))
        instruct_prompt_path = os.path.join(script_dir, '..', 'prompt', 'Instruct_Prompt.md')

        with open(instruct_prompt_path, 'r', encoding='utf-8') as file:
            instruct_prompt_content = file.read()

        combined_text = f"{data['Original']} {data['OriginalLang']} {data['Translated']} {data['TranslatedLang']} {data['EvaluationLang']} {instruct_prompt_content}"
        response = model.generate_content(combined_text)
        raw_text = response.candidates[0].content.parts[0].text
        json_text = raw_text.strip('```json\n').rstrip('```').replace("\n", "\\n")

        temp_result_data = json.loads(json_text)

        print(json_text)

        response_data["data"]["result"] = temp_result_data
        return response_data, 200

    except Exception as e:
        if 'API key not valid' in str(e):
            response_data["StatusCode"] = 4200
            response_data["message"] = "Invalid API Key. Please check API Key."
            return response_data, 400

    return response_data, 200