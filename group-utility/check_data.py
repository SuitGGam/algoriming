import pandas as pd
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경변수에서 설정값 가져오기
CSV_INPUT_PATH = os.getenv('CSV_INPUT_PATH')
CSV_ENCODING = os.getenv('CSV_ENCODING', 'utf-8-sig')

df = pd.read_csv(CSV_INPUT_PATH, encoding=CSV_ENCODING)
print(len(df))   # 행 개수 출력(헤더 제외)
print(df.tail()) # 마지막 5개 행 내용 확인
