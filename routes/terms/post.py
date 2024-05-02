# routes/terms/post.py

import datetime
import os
import sys
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 데이터베이스 설정 로드를 위한 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from env_manage import get_env_variable

# 현재 도메인 URL값을 환경 변수에서 가져오는 부분
domain = get_env_variable('DOMAIN')

# 지원하는 언어 목록을 배열로 저장
supported_languages = ['ko', 'en']

def get_current_utc_time():
    """UTC 타임존 객체를 생성하고 현재 시간을 UTC로 반환하는 함수"""
    utc_timezone = datetime.timezone.utc
    return datetime.datetime.now(utc_timezone).isoformat()

def get_language(request_data):
    """요청된 언어 헤더에서 언어 코드를 추출하여 지원하는 언어 목록에 있는지 확인하고, 해당 언어 코드를 반환하는 함수"""
    # 기본값으로 'en' 설정
    default_language = 'en'
    # 요청 데이터에서 'Accept-Language' 헤더 값 추출
    accept_language = request_data.get("Accept-Language", default_language).lower()
    # 하이픈('-')으로 분할하여 언어 코드만 추출
    language_code = accept_language.split('-', 1)[0]
    # 추출된 언어 코드가 지원하는 언어 목록에 있으면 해당 언어를, 없으면 기본 언어('en')을 반환
    return language_code if language_code in supported_languages else default_language

def post_response(request_data):
    # 요청 데이터가 None이면 빈 딕셔너리로 처리
    request_data = request_data or {}
    language = get_language(request_data)

    # 언어에 맞는 약관 URL 생성
    terms_of_service = f"{domain}/terms/{language}/terms_of_service.md"
    privacy_policy = f"{domain}/terms/{language}/privacy_policy.md"

    response_data = {
        "StatusCode": 200,
        "message": "POST request processed. Hello, world!",
        "data": {
            "RequestTime": get_current_utc_time(),
            "privacy_policy": privacy_policy,
            "terms_of_service": terms_of_service
        }
    }

    return response_data, 200
