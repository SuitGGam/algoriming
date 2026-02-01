from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경변수에서 설정값 가져오기
SOLVEDAC_BASE_URL = os.getenv('SOLVEDAC_BASE_URL')
WEBDRIVER_WAIT_TIME = int(os.getenv('WEBDRIVER_WAIT_TIME', 10))

# 쿼리 리스트 (실버 5 ~ 골드 1, 150명 이상 풀고 한국어로 된 문제)
# 기하학, 물리학, 확률, 임의 정밀도 / 큰 수 연산, 애드 혹 제외
queries = [
    '*s5 s#150.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#ad_hoc',
    '*s4 s#150.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#ad_hoc',
    '*s3 s#150.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#ad_hoc',
    '*s2 s#150.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#ad_hoc',
    '*s1 s#150.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#ad_hoc',
    '*g5 s#150.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#ad_hoc',
    '*g4 s#150.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#ad_hoc',
    '*g3 s#150.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#ad_hoc',
    '*g2 s#150.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#ad_hoc',
    '*g1 s#150.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#ad_hoc'
]

def build_search_url(query):
    from urllib.parse import quote_plus
    encoded_query = quote_plus(query)
    url = f"{SOLVEDAC_BASE_URL}?page=1&query={encoded_query}&sort=random&direction=asc"
    return url

def extract_problem_numbers(driver):
    # 문제 번호가 포함된 td > a[href*='/problem/'] 엘리먼트 찾기
    elements = driver.find_elements(By.CSS_SELECTOR, "td a[href*='/problem/']")
    problems = []
    for elem in elements:
        href = elem.get_attribute('href')
        number = href.split('/')[-1]
        if number not in problems:
            problems.append(number)
    return problems

def main():
    # Chrome headless 옵션 (필요시 headless=False로 변경해 동작 확인 가능)
    options = Options()
    options.add_argument("--headless")  # 창 안 띄우고 실행
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # WebDriver 초기화 (ChromeDriver 경로 환경에 맞게 설정)
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, WEBDRIVER_WAIT_TIME)

    results = {}

    try:
        for query in queries:
            url = build_search_url(query)
            print(f"접속 중: {url}")
            driver.get(url)

            # 문제 테이블이 로드될 때까지 대기 (첫 td a[href*='/problem/'] 요소 하나 이상)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "td a[href*='/problem/']")))

            time.sleep(1)  # 추가 여유 시간

            problems = extract_problem_numbers(driver)

            top20 = problems[:20]
            results[query] = top20

            print(f"[{query}] 상위 20개 문제 번호:")
            print(top20)
            print('='*50)

        # 결과를 필요하면 파일로 저장 가능
        # with open("solvedac_problems_top20.json", "w", encoding="utf-8") as f:
        #     import json
        #     json.dump(results, f, ensure_ascii=False, indent=2)

    finally:
        driver.quit()
    
    return results

if __name__ == "__main__":
    results = main() # 반환값으로 할당

    # s1~s5 정렬 출력
    s_group = []
    for key in results:
        if key.startswith('*s'):
            s_group.extend(results[key])
    # 문자열로 변환 후 정렬
    s_unique_sorted = sorted(set(str(num) for num in s_group), key=int)
    
    print("실버 문제 오름차순:")
    # 리스트를 쉼표와 공백으로 구분된 문자열로 결합하여 출력
    print(", ".join(s_unique_sorted))

    # g1~g5 정렬 출력
    g_group = []
    for key in results:
        if key.startswith('*g'):
            g_group.extend(results[key])
    # 문자열로 변환 후 정렬
    g_unique_sorted = sorted(set(str(num) for num in g_group), key=int)
    
    print("골드 문제 오름차순:")
    # 리스트를 쉼표와 공백으로 구분된 문자열로 결합하여 출력
    print(", ".join(g_unique_sorted))

# 참고: int로 정렬 후 다시 문자열로 join해도 됩니다.
# s_unique_sorted = sorted(set(int(num) for num in s_group))
# print(", ".join(str(num) for num in s_unique_sorted))