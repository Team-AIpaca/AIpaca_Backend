# routes/notice/post.py

import datetime
import os
import sys
import requests
import json
import xmltodict
from flask import request

# 환경 변수 관리 모듈 경로 추가 함수
def add_env_manage_to_path():
    current_file_path = os.path.dirname(os.path.abspath(__file__))
    env_manage_directory = os.path.abspath(os.path.join(current_file_path, os.pardir, os.pardir))
    sys.path.insert(0, env_manage_directory)

add_env_manage_to_path()

from env_manage import get_env_variable

# 사용 가능한 언어 목록 정의
ALLOWED_LANGUAGES = ['en-US', 'ko-KR']  # 예시 목록, 필요에 따라 수정

def get_language_code(request_language):
    """요청된 언어가 허용된 언어 목록에 있는지 확인하고, 아니면 기본 언어로 설정"""
    if request_language not in ALLOWED_LANGUAGES:
        return 'en-US'  # 기본 언어
    return request_language

def get_notice_rss():
    return get_env_variable('NOTICE_RSS_URL')

def get_cache_duration():
    # .env 파일에서 캐시 유지 시간을 불러옵니다. 없으면 180분(3시간)을 기본값으로 사용합니다.
    try:
        cache_duration_minutes = get_env_variable('CACHE_DURATION_MINUTES')
        if cache_duration_minutes is None:
            raise ValueError("CACHE_DURATION_MINUTES is not set.")
    except KeyError:
        cache_duration_minutes = '180'
    return int(cache_duration_minutes) * 60

def ensure_cache_directory_exists():
    cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    return cache_dir

def clean_old_cache_files(cache_dir, valid_cache_files):
    for file in os.listdir(cache_dir):
        cache_file = os.path.join(cache_dir, file)
        if cache_file not in valid_cache_files:
            os.remove(cache_file)

def get_current_utc_time():
    utc_timezone = datetime.timezone.utc
    return datetime.datetime.now(utc_timezone)

def is_cache_valid(cache_file, cache_duration):
    if not os.path.exists(cache_file):
        return False
    cache_time = datetime.datetime.strptime(os.path.basename(cache_file).split('_')[0], '%Y%m%d%H%M%S').replace(tzinfo=datetime.timezone.utc)
    return (get_current_utc_time() - cache_time).total_seconds() < cache_duration

def get_notice_rss_json(request_language):
    cache_dir = ensure_cache_directory_exists()
    cache_duration = get_cache_duration()
    language_code = get_language_code(request_language)  # 언어 코드 검증
    valid_cache_files = []

    for file in sorted(os.listdir(cache_dir), reverse=True):
        if f'_{language_code}.json' in file and is_cache_valid(os.path.join(cache_dir, file), cache_duration):
            cache_file = os.path.join(cache_dir, file)
            valid_cache_files.append(cache_file)
            clean_old_cache_files(cache_dir, valid_cache_files)
            with open(cache_file, 'r') as file:
                return json.load(file)

    headers = {'Accept-Language': language_code}
    response = requests.get(get_notice_rss(), headers=headers)
    xmlString = response.text
    jsonString = json.dumps(xmltodict.parse(xmlString), indent=4)
    
    cache_file_path = os.path.join(cache_dir, get_current_utc_time().strftime('%Y%m%d%H%M%S') + f'_{language_code}.json')  # 캐시 파일 이름에 언어 코드 추가
    with open(cache_file_path, 'w') as file:
        file.write(jsonString)
    
    return json.loads(jsonString)  # JSON 문자열을 파이썬 객체로 변환하여 반환

def post_response(request_data):
    # 프론트엔드 요청에서 Accept-Language 헤더 값 추출
    request_language = request.headers.get('Accept-Language', 'en-US')
    
    notice_data = get_notice_rss_json(request_language)

    response_data = {
        "StatusCode": 200,
        "message": "Successful Notice information request",
        "data": {
            "RequestTime": get_current_utc_time().isoformat(),
            "Notice": notice_data
        }
    }
    return response_data, 200
