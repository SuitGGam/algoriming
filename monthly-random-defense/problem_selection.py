from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 쿼리 리스트 (실버 5 ~ 골드 1, 100명 이상 풀고 한국어로 된 문제)
queries = [
    '*s5 s#100.. %ko',
    '*s4 s#100.. %ko',
    '*s3 s#100.. %ko',
    '*s2 s#100.. %ko',
    '*s1 s#100.. %ko',
    '*g5 s#100.. %ko',
    '*g4 s#100.. %ko',
    '*g3 s#100.. %ko',
    '*g2 s#100.. %ko',
    '*g1 s#100.. %ko'
]

def build_search_url(query):
    from urllib.parse import quote_plus
    encoded_query = quote_plus(query)
    url = f"https://solved.ac/problems?page=1&query={encoded_query}&sort=random&direction=asc"
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
    wait = WebDriverWait(driver, 10)

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
    results = main()  # 반환값으로 할당

    # s1~s5 정렬 출력
    s_group = []
    for key in results:
        if key.startswith('*s'):
            s_group.extend(results[key])
    s_unique_sorted = sorted(set(int(num) for num in s_group))
    print("실버 문제 오름차순:")
    print(s_unique_sorted)

    # g1~g5 정렬 출력
    g_group = []
    for key in results:
        if key.startswith('*g'):
            g_group.extend(results[key])
    g_unique_sorted = sorted(set(int(num) for num in g_group))
    print("골드 문제 오름차순:")
    print(g_unique_sorted)