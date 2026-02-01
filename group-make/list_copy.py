from selenium import webdriver
from selenium.webdriver.common.by import By
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
GROUP_ID_SOURCE = os.getenv('GROUP_ID_SOURCE')
WEBDRIVER_WAIT_TIME = int(os.getenv('WEBDRIVER_WAIT_TIME', 10))
SLEEP_MIN = int(os.getenv('SLEEP_MIN', 1))
SLEEP_MAX = int(os.getenv('SLEEP_MAX', 8))

driver = webdriver.Chrome()  # 크롬 드라이버 위치에 맞게 조정 필요

wait = WebDriverWait(driver, WEBDRIVER_WAIT_TIME)

start_page = 1
results = []

while True:
    url = f'{BAEKJOON_GROUP_WORKBOOK_URL}/{GROUP_ID_SOURCE}/{start_page}'
    driver.get(url)
    time.sleep(random.randint(SLEEP_MIN, SLEEP_MAX))

    try:
        trs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tbody tr')))
    except:
        print(f"페이지 {start_page}의 tbody tr을 찾을 수 없어 종료합니다.")
        break

    max_rows = min(50, len(trs))
    hrefs = []
    for i in range(max_rows):
        a_tag = trs[i].find_elements(By.TAG_NAME, 'td')[2].find_element(By.TAG_NAME, 'a')
        hrefs.append(a_tag.get_attribute('href'))

    for href in hrefs:
        driver.get(href)
        time.sleep(random.randint(SLEEP_MIN, SLEEP_MAX))
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.col-md-12')))

        col_md12_divs = driver.find_elements(By.CSS_SELECTOR, 'div.col-md-12')
        target_div_title_desc = col_md12_divs[2]  # 제목, 설명 div (세 번째)
        target_div_problem = col_md12_divs[3]     # 문제 번호 div (네 번째)

        title = target_div_title_desc.find_element(By.TAG_NAME, 'span').text.strip()
        description = target_div_title_desc.find_element(By.TAG_NAME, 'blockquote').text.strip()

        problem_numbers = []
        tbody_rows = target_div_problem.find_elements(By.CSS_SELECTOR, 'tbody tr')
        for tr in tbody_rows:
            tds = tr.find_elements(By.TAG_NAME, 'td')
            if tds:
                problem_numbers.append(tds[0].text.strip())

        question_str = ', '.join(problem_numbers)

        results.append([title, description, question_str])

        time.sleep(random.randint(SLEEP_MIN, SLEEP_MAX))

    print(f"페이지 {start_page} 완료")
    start_page += 1

driver.quit()

# 수집 완료 후 CSV 저장
csv_output_path = os.getenv('CSV_OUTPUT_PATH')
with open(csv_output_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['제목', '설명', '문제 목록'])
    writer.writerows(results)

print("완료, problemworkbooks_all_pages.csv 저장됨")
