# app.py

from flask import Flask, request, Response, send_from_directory
from flask_cors import CORS
import os
import json
import xmltodict
from dotenv import load_dotenv

# 환경변수 파일(.env) 로드
load_dotenv()

app = Flask(__name__)

# 모든 도메인에서의 요청을 허용하기 위한 CORS 설정
CORS(app)

def response_format(data, status=200, content_type='application/json'):
    if content_type == 'application/xml':
        response = Response(xmltodict.unparse({'response': data}, pretty=True), status=status, mimetype=content_type)
    else:
        response = Response(json.dumps(data), status=status, mimetype=content_type)
    return response

def get_content_type():
    response_format_type = request.args.get('format', 'json').lower()
    return 'application/xml' if response_format_type == 'xml' else 'application/json'

def handle_request(endpoint_path, method):
    content_type = get_content_type()
    module_path = f"routes{endpoint_path.replace('/', '.')}.{method.lower()}"
    method_function = __import__(module_path, fromlist=[''])

    if request.method == 'GET':
        request_params = request.args.to_dict()
        data, status_code = method_function.get_response(request_params)
    else:
        # POST 요청에 대해 JSON 데이터가 필요없을 경우 예외 처리
        try:
            request_data = request.get_json()
        except Exception:
            request_data = None  # JSON 데이터 없이도 요청을 처리할 수 있게 None 할당

        data, status_code = method_function.post_response(request_data)
    return response_format(data, status_code, content_type)

# 공통 라우트 핸들러를 사용하여 엔드포인트 정의
# 서버 연결 확인용 ping 라우트
@app.route('/ping', methods=['GET', 'POST'])
def ping():
    return handle_request('/ping', request.method)

# 언어 감지
@app.route('/api/detectlang', methods=['GET', 'POST'])
def api_detectlang():
    return handle_request('/api/detectlang', request.method)

# 번역 API
# 구글 번역
@app.route('/api/trans/googletrans', methods=['GET', 'POST'])
def api_trans_googletrans():
   return handle_request('/api/trans/googletrans', request.method)

# DeepL
@app.route('/api/trans/deepl', methods=['GET', 'POST'])
def api_trans_deepl():
   return handle_request('/api/trans/deepl', request.method)

# LibreTranslate
@app.route('/api/trans/libretranslate', methods=['GET', 'POST'])
def api_trans_libretranslate():
   return handle_request('/api/trans/libretranslate', request.method)

# 번역 평가
## Gemini
@app.route('/api/evaluation/gemini', methods=['GET', 'POST'])
def api_evaluation_gemini():
    return handle_request('/api/evaluation/gemini', request.method)

## GPT
@app.route('/api/evaluation/gpt', methods=['GET', 'POST'])
def api_evaluation_gpt():
    return handle_request('/api/evaluation/gpt', request.method)

# 회원가입
@app.route('/api/user/signup', methods=['GET', 'POST'])
def api_user_signup():
    return handle_request('/api/user/signup', request.method)

# 약관 정보
@app.route('/terms', methods=['GET', 'POST'])
def terms():
    return handle_request('/terms', request.method)

# 마크다운 파일을 직접 제공하는 엔드포인트를 추가
@app.route('/terms/<path:filename>', methods=['GET', 'POST'])
def terms_of_service(filename):
    # 안전하게 파일 경로를 구성하기 위해 os.path.join 사용
    return send_from_directory(os.path.join(app.root_path, 'terms'), filename)

# 로그인
@app.route('/api/user/login', methods=['GET', 'POST'])
def api_user_login():
    return handle_request('/api/user/login', request.method)

# 도전 과제
## 도전 과제 달성
@app.route('/api/challenge/achieve', methods=['GET', 'POST'])
def api_challenge_achieve():
    return handle_request('/api/challenge/achieve', request.method)

## 도전 과제 달성 목록
@app.route('/api/challenge/verify', methods=['GET', 'POST'])
def api_challenge_verify():
    return handle_request('/api/challenge/verify', request.method)

# 서비스 버전 정보
@app.route('/version', methods=['GET', 'POST'])
def version():
    return handle_request('/version', request.method)

# 백업
@app.route('/api/data/backup', methods=['GET', 'POST'])
def notice():
    return handle_request('/api/data/backup', request.method)

# 복원
@app.route('/api/data/restore', methods=['GET', 'POST'])
def notice():
    return handle_request('/api/data/restore', request.method)

# 공지사항
@app.route('/notice', methods=['GET', 'POST'])
def notice():
    return handle_request('/notice', request.method)

# 기타 엔드포인트를 여기에 추가...

if __name__ == '__main__':
    port = os.getenv('FLASK_RUN_PORT', 5000)
    # 멀티스레드 옵션 활성화하여 Flask 내장 서버 사용
    app.run(debug=True, port=port, threaded=True)
