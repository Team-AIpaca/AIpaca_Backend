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

def get_notice_rss():
    return get_env_variable('NOTICE_RSS_URL')

def get_cache_duration():
    # .env 파일에서 캐시 유지 시간을 불러옵니다. 없으면 180분(3시간)을 기본값으로 사용합니다.
    try:
        cache_duration_minutes = get_env_variable('CACHE_DURATION_MINUTES')
        if cache_duration_minutes is None:  # get_env_variable 함수가 None을 반환할 수도 있는 경우 대비
            raise ValueError("CACHE_DURATION_MINUTES is not set.")
    except KeyError:  # 변수가 .env 파일에 없는 경우
        cache_duration_minutes = '180'  # 기본값
    return int(cache_duration_minutes) * 60  # 분을 초로 변환

def ensure_cache_directory_exists():
    cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    return cache_dir

def clean_old_cache_files(cache_dir, valid_cache_file):
    for file in os.listdir(cache_dir):
        cache_file = os.path.join(cache_dir, file)
        if cache_file != valid_cache_file:  # 유효한 캐시 파일은 제외하고 삭제
            os.remove(cache_file)

def is_cache_valid(cache_file, cache_duration):
    if not os.path.exists(cache_file):
        return False
    # UTC 시간대 정보를 포함하여 datetime 객체 생성
    cache_time = datetime.datetime.strptime(os.path.basename(cache_file).replace('.json', ''), '%Y%m%d%H%M%S').replace(tzinfo=datetime.timezone.utc)
    return (get_current_utc_time() - cache_time).total_seconds() < cache_duration  # 설정된 캐시 시간 이내인지 확인

def get_notice_rss_json(request_language):
    cache_dir = ensure_cache_directory_exists()
    cache_duration = get_cache_duration()
    
    for file in sorted(os.listdir(cache_dir), reverse=True):
        cache_file = os.path.join(cache_dir, file)
        if is_cache_valid(cache_file, cache_duration):
            clean_old_cache_files(cache_dir, cache_file)
            with open(cache_file, 'r') as file:
                return file.read()

    # 요청 헤더에 Accept-Language 추가, 프론트엔드에서 전달받은 언어 사용
    headers = {
        'Accept-Language': request_language
    }
    
    response = requests.get(get_notice_rss(), headers=headers)
    xmlString = response.text
    jsonString = json.dumps(xmltodict.parse(xmlString), indent=4)
    
    clean_old_cache_files(cache_dir, None)
    
    cache_file_path = os.path.join(cache_dir, get_current_utc_time().strftime('%Y%m%d%H%M%S') + '.json')
    with open(cache_file_path, 'w') as file:
        file.write(jsonString)
    
    return json.loads(jsonString)

def get_current_utc_time():
    utc_timezone = datetime.timezone.utc
    return datetime.datetime.now(utc_timezone)

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
