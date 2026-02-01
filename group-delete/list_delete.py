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
BAEKJOON_GROUP_WORKBOOK_URL = os.getenv('BAEKJOON_GROUP_WORKBOOK_URL')
GROUP_ID_TARGET = os.getenv('GROUP_ID_TARGET')
WEBDRIVER_WAIT_TIME = int(os.getenv('WEBDRIVER_WAIT_TIME', 10))
SLEEP_MIN = int(os.getenv('SLEEP_MIN', 1))
SLEEP_MAX = int(os.getenv('SLEEP_MAX', 8))

driver = webdriver.Chrome()
wait = WebDriverWait(driver, WEBDRIVER_WAIT_TIME)

group_url = f"{BAEKJOON_GROUP_WORKBOOK_URL}/{GROUP_ID_TARGET}"

# 로그인 수동
driver.get(BAEKJOON_LOGIN_URL)
print("로그인 후 10초 대기합니다...")
time.sleep(10)

while True:
    driver.get(group_url)
    time.sleep(random.randint(SLEEP_MIN, SLEEP_MAX))

    try:
        # 1️⃣ 첫 번째 문제집 링크 찾기
        first_workbook = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
            "body > div.wrapper > div.container.content > div > div:nth-child(4) > div > table > tbody > tr:nth-child(1) > td:nth-child(3) > a"
        )))
        href = first_workbook.get_attribute("href")
        print(f"문제집 진입: {href}")
        driver.get(href)
        time.sleep(random.randint(1, 2))

        # 2️⃣ 삭제 페이지로 이동 버튼 클릭
        delete_page_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
            "body > div.wrapper > div.container.content > div > div:nth-child(4) > blockquote > div > a"
        )))
        delete_page_btn.click()
        time.sleep(random.randint(SLEEP_MIN, SLEEP_MAX))

        # 3️⃣ 삭제 버튼 클릭 → 브라우저 prompt 발생
        delete_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#delete_button")))
        delete_btn.click()
        time.sleep(0.7)

        # 4️⃣ JS prompt에 "삭제합니다" 입력 후 확인
        alert = driver.switch_to.alert
        print("⚠️ 확인창 발생:", alert.text)
        alert.send_keys("삭제합니다")
        alert.accept()
        print("✅ '삭제합니다' 입력 후 확인 클릭 완료")

        time.sleep(random.randint(SLEEP_MIN, SLEEP_MAX))
        print("✅ 문제집 삭제 완료. 다음 문제집으로 이동합니다...")

    except Exception as e:
        print("⚠️ 더 이상 문제집이 없거나 오류 발생. 종료합니다.")
        print(e)
        break

driver.quit()
print("🎉 모든 문제집 삭제 완료.")
