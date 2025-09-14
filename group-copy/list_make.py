import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

# CSV 파일 읽기 (encoding utf-8-sig)
df = pd.read_csv('problemworkbooks_all_pages_edit.csv', encoding='utf-8-sig')

driver = webdriver.Chrome()  # 크롬 드라이버 환경에 맞게 설정

wait = WebDriverWait(driver, 15)  # 최대 15초 명시적 대기

# 1. 로그인 페이지 열기 및 수동 로그인 대기
driver.get("https://www.acmicpc.net/login")
print("로그인 후 5초 대기합니다...")
time.sleep(5)

# 2. CSV 역순으로 문제집 생성 자동화
for idx, row in df[::-1].iterrows():
    driver.get("https://www.acmicpc.net/group/workbook/create/23757")
    time.sleep(random.randint(3, 8))  # 페이지 안정화 대기

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
        time.sleep(0.1)

    # 문제집 생성 버튼 클릭
    create_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-primary")))
    create_btn.click()

    time.sleep(random.randint(3, 8))

driver.quit()
