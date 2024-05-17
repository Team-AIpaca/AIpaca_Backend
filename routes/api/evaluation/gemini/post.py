import requests
import json
import datetime
import os
import re
from flask import request

# 언어 코드 확인 API 주소
check_lang_code = "https://apis.uiharu.dev/trans/api2.php"

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
        field_value = str(request_data.get(field, "")).strip().lower()  # 필드 값을 소문자로 변환 및 공백 제거
        # 문자열 시작 부분에서 금지된 단어가 바로 나오는 경우만 검사
        for disallowed_word in disallowed_words:
            # 패턴: 문자열 시작 부분에서 바로 금지된 단어가 나오고, 그 뒤에 바로 문자열 끝나는 경우
            pattern = rf"^{disallowed_word}$"
            if re.match(pattern, field_value, re.IGNORECASE):  # 대소문자 무시하고 검색
                response_data["StatusCode"] = 4004
                response_data["message"] = f"A value is not allowed in {field}: {request_data[field]}"
                return response_data, 400
            # 문자열의 시작 부분이 금지된 단어인 경우
            if field_value.startswith(disallowed_word):  # 금지된 단어로 시작하는 경우에 앞에 공백 추가
                request_data[field] = " " + request_data[field]
                
    # 언어 코드 검증
    headers = {'Content-Type': 'application/json'}
    original_lang_check = requests.post(
        check_lang_code,
        json={"transSentence": data['Original'], "targetLang": "ko"},
        headers=headers
    )
    translated_lang_check = requests.post(
        check_lang_code,
        json={"transSentence": data['Translated'], "targetLang": "ko"},
        headers=headers
    )

    if original_lang_check.status_code == 200 and translated_lang_check.status_code == 200:
        original_lang_result = original_lang_check.json()['detectedLanguage']
        translated_lang_result = translated_lang_check.json()['detectedLanguage']
        
        # 언어 코드 검증 전 데이터 정규화
        normalized_original_lang = data['OriginalLang'].strip().lower()
        normalized_translated_lang = data['TranslatedLang'].strip().lower()

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

            # JSON을 올바르게 파싱하기 위해 올바른 방법으로 텍스트를 잘라내기
            json_start = raw_text.find("{")
            json_end = raw_text.rfind("}") + 1
            cleaned_text = raw_text[json_start:json_end]
            
            try:
                # JSON 문자열 파싱 시도
                result_data = json.loads(cleaned_text)
                response_data["data"]["result"] = result_data
            except json.JSONDecodeError:
                try:
                    # 두 번째 JSON 파싱 시도
                    cleaned_text = cleaned_text.replace('\n', '').replace('    ', '')  # 개행 문자와 들여쓰기 제거
                    result_str_escaped = cleaned_text.encode().decode('unicode_escape')
                    result_data = json.loads(result_str_escaped)
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
