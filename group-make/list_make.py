import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경변수에서 설정값 가져오기
BAEKJOON_LOGIN_URL = os.getenv('BAEKJOON_LOGIN_URL')
BAEKJOON_WORKBOOK_CREATE_URL = os.getenv('BAEKJOON_WORKBOOK_CREATE_URL')
GROUP_ID_CREATE = os.getenv('GROUP_ID_CREATE')
CSV_INPUT_PATH = os.getenv('CSV_INPUT_PATH')
CSV_ENCODING = os.getenv('CSV_ENCODING', 'utf-8-sig')
WEBDRIVER_WAIT_TIME = int(os.getenv('WEBDRIVER_WAIT_TIME', 10))
SLEEP_MIN = int(os.getenv('SLEEP_MIN', 1))
SLEEP_MAX = int(os.getenv('SLEEP_MAX', 7))

# CSV 파일 읽기
df = pd.read_csv(CSV_INPUT_PATH, encoding=CSV_ENCODING)

driver = webdriver.Chrome()  # 크롬 드라이버 환경에 맞게 설정

wait = WebDriverWait(driver, WEBDRIVER_WAIT_TIME)  # 최대 시간 명시적 대기

# 1. 로그인 페이지 열기 및 수동 로그인 대기
driver.get(BAEKJOON_LOGIN_URL)
print("로그인 후 10초 대기합니다...")
time.sleep(10)

# 2. CSV 역순으로 문제집 생성 자동화
# 중간에 끊겼을 때 이어서 하기는 🔽아래 주석
# for idx, row in df.iloc[0:93][::-1].iterrows():
# 처음부터 끝까지는 🔽아래 주석
for idx, row in df[::-1].iterrows():
    create_url = f"{BAEKJOON_WORKBOOK_CREATE_URL}/{GROUP_ID_CREATE}"
    driver.get(create_url)
    time.sleep(random.randint(SLEEP_MIN, SLEEP_MAX))  # 페이지 안정화 대기

    # NaN 처리
    title = row['제목'] if isinstance(row['제목'], str) else ""
    description = row['설명'] if isinstance(row['설명'], str) else ""
    problem_str = row['문제 목록'] if isinstance(row['문제 목록'], str) else ""

    print(f"제목: {title}, 설명: {description}, 문제 목록: {problem_str}")

    # 제목 입력 (CSS selector 직접 사용)
    title_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 
        "body > div.wrapper > div.container.content > div.row > form > div.col-md-4 > div:nth-child(1) > div > input")))
    title_input.clear()
    title_input.send_keys(title)

    # 설명 입력
    desc_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 
        "body > div.wrapper > div.container.content > div.row > form > div.col-md-4 > div:nth-child(2) > div > input")))
    desc_input.clear()
    desc_input.send_keys(description)

    # 문제 번호 입력
    problem_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 
        "body > div.wrapper > div.container.content > div.row > form > div.col-md-8 > div.form-group > div > input")))

    probs = [p.strip() for p in problem_str.split(',') if p.strip()]
    for prob in probs:
        problem_input.clear()  # clear() 필요 없으면 제거 가능
        problem_input.send_keys(prob)
        problem_input.send_keys(Keys.ENTER)
        time.sleep(0.05)

    # 문제집 생성 버튼 클릭
    time.sleep(0.5)
    create_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-primary")))
    create_btn.click()

    time.sleep(random.randint(1, 4))

driver.quit()
