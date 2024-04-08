# routes/api/evaluation/gpt/post.py

import datetime
import os
import sys
import json
from flask import request
import requests
import openai  # OpenAI GPT를 사용하기 위한 패키지 임포트
import openai.error  # OpenAI 에러 처리를 위한 모듈 임포트

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
        "message": "Success to request to GPT!",
        "data": {
            "RequestTime": get_current_utc_time()
        }
    }

    data = request.get_json() or request_data
    required_fields = ['OpenAIAPIKey', 'GPTVersion', 'Original', 'OriginalLang', 'Translated', 'TranslatedLang', 'EvaluationLang']
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
        # OpenAI API 키 설정
        openai.api_key = data['OpenAIAPIKey']
        # GPT 모델 버전에 따라 모델 선택
        model = f"gpt-{data['GPTVersion']}"

        prompt = (f"{data['Original']} {data['OriginalLang']} "
                  f"{data['Translated']} {data['TranslatedLang']} "
                  f"{data['EvaluationLang']}")

        # GPT API를 사용하여 콘텐츠 생성
        response = openai.Completion.create(
            engine=model,
            prompt=prompt,
            # max_tokens=150 # 최대 토큰수
        )

        # 응답에서 생성된 텍스트 추출
        generated_text = response.choices[0].text.strip()

        # 생성된 텍스트를 JSON 형식으로 변환하려고 시도
        try:
            # JSON 문자열을 JSON 객체로 변환
            result_json = json.loads(generated_text)

            # 성공 시 결과 데이터 추가
            response_data["data"]["result"] = result_json
            return response_data, 200
        except json.JSONDecodeError:
            response_data["StatusCode"] = 500
            response_data["message"] = "Failed to decode generated text as JSON"
            return response_data, 500

    except openai.error.AuthenticationError:
        # OpenAI API 키 인증 실패 에러 처리
        response_data["StatusCode"] = 401
        response_data["message"] = "Invalid OpenAI API Key"
        return response_data, 401
    except Exception as e:
        response_data["StatusCode"] = 500
        response_data["message"] = f"An error occurred: {str(e)}"
        return response_data, 500

    return response_data, 200
