from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from urllib.parse import quote_plus

def build_search_url(query):
    encoded_query = quote_plus(query)
    return f"https://solved.ac/problems?page=1&query={encoded_query}&sort=random&direction=asc"

def extract_problem_numbers(driver):
    elements = driver.find_elements(By.CSS_SELECTOR, "td a[href*='/problem/']")
    problems = []
    for elem in elements:
        href = elem.get_attribute('href')
        num = int(href.split('/')[-1])
        problems.append(num)
    return problems

def get_non_overlapping_n(driver, wait, query, exclude_numbers, n=2, max_attempts=20):
    """한 쿼리 안에서 제외 리스트 기반으로 n개 문제를 랜덤하게 뽑는 함수"""
    exclude_set = set(exclude_numbers)
    for _ in range(max_attempts):
        driver.get(build_search_url(query))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "td a[href*='/problem/']")))
        time.sleep(1)
        problems = extract_problem_numbers(driver)
        filtered = [p for p in problems if p not in exclude_set]
        if len(filtered) >= n:
            return filtered[:n]
    return []

def get_unique_problems_for_group(driver, wait, queries, exclude_numbers, group_name):
    results = {}
    chosen = set(exclude_numbers)

    for query in queries:
        problem = None
        retry_count = 0
        # 🔁 쿼리 단위로 최대 5번 재시도
        while problem is None and retry_count < 5:
            for _ in range(30):  # 페이지 랜덤 요청 30회
                problems = get_non_overlapping_n(driver, wait, query, chosen, n=1)
                if not problems:
                    continue
                candidate = problems[0]
                if candidate not in chosen:
                    problem = candidate
                    break
            retry_count += 1

        results[query] = problem
        if problem:
            chosen.add(problem)
            print(f"{group_name} : [{query}] 선택된 문제: {problem}")
        else:
            print(f"⚠️ {group_name} 쿼리 실패: {query}")

        print("=" * 50)

    return results


def main():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    # 쿼리 리스트 (실버 5 ~ 실버 1 + 실버 전체 2, 200명 이상 풀고 한국어로 된 문제)
    # 기하학, 물리학, 확률, 임의 정밀도 / 큰 수 연산, 수학 제외
    queries_silver = [
        '*s5 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math',
        '*s4 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math',
        '*s3 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math',
        '*s2 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math',
        '*s1 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math',
        '*s s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math',
        '*s s#201.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math'
    ]

    # 제외할 문제 번호 리스트 (실버)
    exclude_numbers_silver = [
        1149, 1189, 1343, 1590, 1620, 1783, 1920, 1985, 2075, 2108, 2161, 2232, 2428, 2468, 2583, 2594, 2606, 2853, 2870, 2876, 2890, 2961, 2993, 3036, 3049, 3054, 3135, 3216, 3896, 4358, 5619, 5623, 7696, 8394, 9012, 9196, 9461, 9657, 10211, 10571, 10816, 10973, 11055, 11057, 11059, 11725, 11726, 11971, 12981, 13241, 13270, 13301, 13333, 13417, 13700, 14600, 14713, 15736, 15887, 15900, 15992, 16165, 16174, 16196, 16435, 16955, 16956, 17254, 17359, 18115, 18311, 19622, 20152, 21557, 21967, 22941, 23797, 24523, 24725, 25287, 25418, 25421, 25966, 26122, 27952, 27967, 28279, 28324, 30458, 30506, 31287, 31674, 32206, 32291, 32630, 33575, 33684, 33756, 33846, 33991,
        1439, 1904, 9291, 11508, 20167, 31462, 33613,
        11004, 13903, 16439, 21737, 23561, 24060, 31670,
        9414, 9536, 10867, 12101, 14594, 25758, 27497
    ]

    # 쿼리 리스트 (골드 5 ~ 골드 1 + 골드 전체 2, 200명 이상 풀고 한국어로 된 문제)
    # 기하학, 물리학, 확률, 임의 정밀도 / 큰 수 연산, 수학 제외
    queries_gold = [
        '*g5 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math',
        '*g4 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math',
        '*g3 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math',
        '*g2 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math',
        '*g1 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math',
        '*g s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math',
        '*g s#201.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math'
    ]

    # 제외할 문제 번호 리스트 (골드)
    exclude_numbers_gold = [
        1035, 1045, 1079, 1099, 1117, 1208, 1242, 1450, 1636, 1663, 1753, 1818, 1898, 2014, 2021, 2091, 2138, 2176, 2224, 2228, 2233, 2234, 2253, 2268, 2370, 2459, 2551, 2580, 2694, 2733, 3980, 4233, 4920, 5463, 6137, 6503, 7569, 7579, 7976, 9084, 9251, 9464, 10830, 10838, 10840, 11442, 12015, 12107, 13911, 14257, 14550, 14718, 14728, 14864, 14867, 15683, 15732, 15976, 15999, 16398, 16563, 16678, 16947, 17069, 17090, 17302, 17370, 17404, 17954, 18224, 19237, 19539, 19566, 20164, 21611, 21775, 22253, 22345, 22358, 23059, 23250, 23747, 23835, 23845, 23889, 24041, 24391, 24526, 25181, 25319, 28069, 28218, 28284, 28707, 30035, 30460, 30689, 31413, 31965, 33615,
        1327, 1944, 2195, 4386, 10564, 11578, 22944,
        1800, 2457, 2479, 5427, 5550, 26009, 30960,
        1700, 8972, 11049, 12915, 20047, 20191, 30461
    ]

    try:
        # 실버 그룹 7문제 고유하게 추출
        silver_results = get_unique_problems_for_group(driver, wait, queries_silver, exclude_numbers_silver, "실버")
        gold_results = get_unique_problems_for_group(driver, wait, queries_gold, exclude_numbers_gold, "골드")

        # 정렬 및 출력
        s_unique_sorted = sorted(set(p for p in silver_results.values() if p))
        g_unique_sorted = sorted(set(p for p in gold_results.values() if p))

        print("\n실버 문제 :")
        print(s_unique_sorted)

        print("\n골드 문제 :")
        print(g_unique_sorted)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
