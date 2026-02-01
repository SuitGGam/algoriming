import chardet
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경변수에서 설정값 가져오기
CSV_INPUT_PATH = os.getenv('CSV_INPUT_PATH')

with open(CSV_INPUT_PATH, 'rb') as f:
    rawdata = f.read(10000)  # 샘플 읽기
    result = chardet.detect(rawdata)
    print(result)
