# routes/api/evaluation/gemini/post.py

import requests
import json
import datetime
import os
import sys
import re
from flask import request

# 현재 파일의 절대 경로를 구합니다.
current_file_path = os.path.abspath(__file__)

# 현재 파일로부터 상위 4개 디렉토리로 이동하여 env_manage.py가 위치한 디렉토리의 경로를 구합니다.
env_manage_directory = os.path.join(current_file_path, '../../../../')

# 이 경로를 sys.path에 추가합니다.
sys.path.insert(0, env_manage_directory)

# 이제 env_manage.py를 임포트할 수 있습니다.
from env_manage import get_env_variable

def get_current_utc_time():
    utc_timezone = datetime.timezone.utc
    return datetime.datetime.now(utc_timezone).isoformat()

def calculate_max_output_tokens(translated_text, base_ratio=1.5):
    translated_tokens = len(translated_text.split())
    max_output_tokens = int(translated_tokens * base_ratio)
    max_output_tokens = max(150, min(max_output_tokens, 2048))
    return max_output_tokens

def post_response(request_data):
    response_data = {
        "StatusCode": 200,
        "message": "Success to request to Gemini!",
        "data": {
            "RequestTime": get_current_utc_time()
        }
    }

    data = request_data
    # 필수 필드
    required_fields = ['GeminiAPIKey', 'Original', 'OriginalLang', 'Translated', 'TranslatedLang', 'EvaluationLang']
    # 검사할 금지된 단어 목록
    disallowed_words = ['TranslatedLang', 'GeminiAPIKey', 'Original', 'OriginalLang', 'Translated', 'EvaluationLang', 'StatusCode', 'message', 'data', 'RequestTime', 'result']
    missing_fields = [field for field in required_fields if field not in data]
    unknown_params = [field for field in data if field not in required_fields]

    if not data.get('GeminiAPIKey', '').strip():
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
    
    # 필수 필드들의 값에서 금지된 단어가 있는지 검사
    for field in required_fields:
        # 필드 값 가져오기, 값이 없다면 빈 문자열을 사용
        value = str(request_data.get(field, "")).strip().lower()
        # 금지된 단어가 포함되어 있는지 검사
        if any(disallowed_word.lower() in value for disallowed_word in disallowed_words):
            response_data["StatusCode"] = 4004
            response_data["message"] = f"A value is not allowed in {field}: {request_data[field]}"
            return response_data, 400

    try:
        GOOGLE_API_KEY = data['GeminiAPIKey']
        
         # 파일 읽기
        script_dir = os.path.dirname(os.path.abspath(__file__))
        instruct_prompt_path = os.path.join(script_dir, '..', 'prompt', 'Instruct_Prompt.md')
        with open(instruct_prompt_path, 'r', encoding='utf-8') as file:
            instruct_prompt_content = file.read()
        
        # 요청한 값 중, GeminiAPIKey를 제외한 나머지 키들을 combined_text_json에 저장
        combined_text_json = json.dumps({
            "Original": data['Original'],
            "OriginalLang": data['OriginalLang'],
            "Translated": data['Translated'],
            "TranslatedLang": data['TranslatedLang'],
            "EvaluationLang": data['EvaluationLang']
        }, ensure_ascii=False)  # ensure_ascii=False 옵션으로 유니코드 문자가 이스케이프되지 않도록 함

        # combined_text의 최종 형태: JSON 문자열과 Instruct_Prompt.md 내용을 포함
        combined_text = f"{combined_text_json}\n{instruct_prompt_content}"
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={GOOGLE_API_KEY}"
        
        headers = {'Content-Type': 'application/json'}
        
        payload = {
            "contents": [{
                "parts": [{"text": combined_text }]
            }],
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ],
            "generationConfig": {
                "temperature": 0.4,
                "topP": 0.8,
                "topK": 45,
            }
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            response_json = response.json()
            raw_text = response_json['candidates'][0]['content']['parts'][0]['text']

            # ```json\n와 \n```을 제거합니다. 이 과정에서 리터럴 개행 문자 변환은 수행하지 않습니다.
            # cleaned_text = raw_text.strip('` \n').lstrip('json\n')
            cleaned_text = raw_text[7+1:-5]
            
            print(cleaned_text)

            try:
                # JSON 문자열 파싱 시도
                result_data = json.loads(cleaned_text)

                # 성공적으로 파싱된 결과를 response_data에 할당
                response_data["data"]["result"] = result_data
            except json.JSONDecodeError as e:
                # JSON 파싱 오류 처리
                response_data["StatusCode"] = 500
                response_data["message"] = f"Error parsing JSON: {str(e)}"
                response_data["data"]["result"] = cleaned_text  # 오류 발생 시 원본 텍스트를 반환
                return response_data, 500

            return response_data, 200
        else:
            response_data["StatusCode"] = response.status_code
            response_data["message"] = "Error from Gemini API: " + response.text
            return response_data, response.status_code

    except Exception as e:
        if 'API key not valid' in str(e):
            response_data["StatusCode"] = 4200
            response_data["message"] = "Invalid API Key. Please check API Key."
            return response_data, 400
        else:
            response_data["StatusCode"] = 500
            response_data["message"] = f"Unknown error occurred: {str(e)}"
            return response_data, 500

    return response_data, 200