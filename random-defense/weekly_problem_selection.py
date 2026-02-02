from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

SOLVEDAC_BASE_URL = os.getenv('SOLVEDAC_BASE_URL')
WEBDRIVER_WAIT_TIME = int(os.getenv('WEBDRIVER_WAIT_TIME', 10))
EXCLUDE_SILVER_PATH = os.getenv('EXCLUDE_SILVER_PATH')
EXCLUDE_GOLD_PATH = os.getenv('EXCLUDE_GOLD_PATH')

def load_exclude_list(file_path):
    """파일에서 문제 번호들을 읽어와서 set으로 반환"""
    if not file_path or not os.path.exists(file_path):
        return set()
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # 정규표현식으로 모든 숫자 덩어리 추출
        numbers = re.findall(r'\d+', content)
        return set(map(int, numbers))

def save_new_problems(file_path, new_problems):
    """새로 선택된 문제 번호들을 한 줄에 쉼표로 구분하여 추가"""
    if not file_path or not new_problems:
        return
    
    # 숫자들을 정렬한 뒤 "123, 456, 789" 형태의 문자열로 변환
    problems_str = ", ".join(map(str, sorted(new_problems)))
    
    with open(file_path, 'a', encoding='utf-8') as f:
        # 파일이 비어있지 않다면 줄바꿈 후 저장, 비어있다면 바로 저장
        # 파일 크기를 확인하여 줄바꿈 여부 결정
        if os.path.getsize(file_path) > 0:
            f.write(f"\n{problems_str}")
        else:
            f.write(problems_str)

def build_search_url(query):
    encoded_query = quote_plus(query)
    return f"{SOLVEDAC_BASE_URL}?page=1&query={encoded_query}&sort=random&direction=asc"

def extract_problem_numbers(driver):
    elements = driver.find_elements(By.CSS_SELECTOR, "td a[href*='/problem/']")
    problems = []
    for elem in elements:
        href = elem.get_attribute('href')
        num = int(href.split('/')[-1])
        problems.append(num)
    return problems

def get_non_overlapping_n(driver, wait, query, exclude_set, n=1, max_attempts=20):
    for _ in range(max_attempts):
        driver.get(build_search_url(query))
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "td a[href*='/problem/']")))
            time.sleep(1)
            problems = extract_problem_numbers(driver)
            filtered = [p for p in problems if p not in exclude_set]
            if len(filtered) >= n:
                return filtered[:n]
        except:
            continue
    return []

def get_unique_problems_for_group(driver, wait, queries, initial_exclude_set, group_name):
    results = {}
    current_chosen = initial_exclude_set.copy()

    for query in queries:
        problem = None
        retry_count = 0
        while problem is None and retry_count < 5:
            for _ in range(30):
                problems = get_non_overlapping_n(driver, wait, query, current_chosen, n=1)
                if problems:
                    candidate = problems[0]
                    problem = candidate
                    break
            retry_count += 1

        results[query] = problem
        if problem:
            current_chosen.add(problem)
            print(f"{group_name} : [{query}] 선택된 문제: {problem}")
        else:
            print(f"⚠️ {group_name} 쿼리 실패: {query}")
        print("-" * 30)

    return results

def main():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, WEBDRIVER_WAIT_TIME)

    # 1. 파일에서 제외 목록 로드
    exclude_numbers_silver = load_exclude_list(EXCLUDE_SILVER_PATH)
    exclude_numbers_gold = load_exclude_list(EXCLUDE_GOLD_PATH)

    queries_silver = [
        '*s5 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math',
        '*s4 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math',
        '*s3 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math',
        '*s2 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math',
        '*s1 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math',
        '*s s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math',
        '*s s#201.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math'
    ]

    queries_gold = [
        '*g5 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math -#ad_hoc',
        '*g4 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math -#ad_hoc',
        '*g3 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math -#ad_hoc',
        '*g2 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math -#ad_hoc',
        '*g1 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math -#ad_hoc',
        '*g s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math -#ad_hoc',
        '*g s#201.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math -#ad_hoc'
    ]

    try:
        silver_results = get_unique_problems_for_group(driver, wait, queries_silver, exclude_numbers_silver, "실버")
        gold_results = get_unique_problems_for_group(driver, wait, queries_gold, exclude_numbers_gold, "골드")

        s_selected = [p for p in silver_results.values() if p]
        g_selected = [p for p in gold_results.values() if p]

        print("\n=== 최종 선택 결과 ===")
        print(f"실버: {sorted(s_selected)}")
        print(f"골드: {sorted(g_selected)}")

        # 2. 새로 뽑힌 문제를 파일에 자동으로 추가 (업데이트)
        save_new_problems(EXCLUDE_SILVER_PATH, s_selected)
        save_new_problems(EXCLUDE_GOLD_PATH, g_selected)
        print("\n✅ 제외 목록 파일이 업데이트되었습니다.")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()