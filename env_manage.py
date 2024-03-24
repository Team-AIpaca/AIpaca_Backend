# env_manage.py
from dotenv import load_dotenv
import os

# .env 파일의 경로를 설정합니다. 이 경로는 프로젝트 루트 디렉토리 내의 .env 파일로 지정됩니다.
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

# .env 파일을 로드합니다.
load_dotenv(dotenv_path)

def get_env_variable(name):
    """
    환경 변수의 값을 가져오는 함수입니다.
    
    :param name: 환경 변수의 이름
    :return: 환경 변수의 값. 만약 변수가 없다면 None을 반환합니다.
    """
    return os.getenv(name)
