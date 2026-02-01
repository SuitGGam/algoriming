from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경변수에서 설정값 가져오기
SOLVEDAC_BASE_URL = os.getenv('SOLVEDAC_BASE_URL')
WEBDRIVER_WAIT_TIME = int(os.getenv('WEBDRIVER_WAIT_TIME', 10))

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
    wait = WebDriverWait(driver, WEBDRIVER_WAIT_TIME)

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
        1120, 1183, 1475, 1543, 1544, 1564, 1713, 1900, 1996, 2004, 2217, 2564, 2824, 3216, 3699, 3961, 4881, 5393, 5567, 6615, 9020, 9048, 9237, 9372, 9414, 9549, 9659, 10253, 10844, 10895, 11652, 11971, 12026, 12782, 12968, 13414, 13717, 13900, 13908, 14646, 14674, 14916, 15312, 15650, 16206, 16463, 16713, 16723, 17123, 17212, 17245, 17264, 17266, 17479, 18126, 18352, 20301, 20413, 22858, 23253, 24090, 24392, 25185, 25206, 25312, 25329, 25371, 25421, 26006, 26071, 27295, 28075, 28110, 28238, 28279, 29715, 29718, 29723, 30457, 30618, 30619, 30645, 30980, 31263, 31460, 31869, 31910, 32185, 32248, 32281, 32931, 33042, 33524, 33559, 33677, 33710, 34042, 34075, 34146, 34705,
        2535, 14244, 16510, 20114, 20438, 26215, 27495,
        5464, 9079, 14494, 16173, 18222, 25644, 28088,
        1755, 1927, 2659, 3407, 7795, 26042, 31924,
        1895, 2792, 20310, 22351, 26150, 27967, 28065,
        2290, 2890, 10656, 14889, 20291, 28446, 32372,
        1347, 2817, 2840, 25918, 29155, 29615, 32172,
        1544, 8979, 9733, 13702, 16564, 17390, 27112,
        1543, 3986, 9934, 21394, 23757, 25418, 28464,
        2823, 11651, 15810, 20551, 23305, 28422, 34099,
        1439, 1904, 9291, 11508, 20167, 31462, 33613,
        11004, 13903, 16439, 21737, 23561, 24060, 31670,
        9414, 9536, 10867, 12101, 14594, 25758, 27497
    ]

    # 쿼리 리스트 (골드 5 ~ 골드 1 + 골드 전체 2, 200명 이상 풀고 한국어로 된 문제)
    # 기하학, 물리학, 확률, 임의 정밀도 / 큰 수 연산, 수학, 애드 혹 제외
    queries_gold = [
        '*g5 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math -#ad_hoc',
        '*g4 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math -#ad_hoc',
        '*g3 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math -#ad_hoc',
        '*g2 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math -#ad_hoc',
        '*g1 s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math -#ad_hoc',
        '*g s#200.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math -#ad_hoc',
        '*g s#201.. %ko -#geometry -#physics -#probability -#arbitrary_precision -#math -#ad_hoc'
    ]

    # 제외할 문제 번호 리스트 (골드)
    exclude_numbers_gold = [
        1035, 1041, 1119, 1234, 1277, 1285, 1419, 1477, 1548, 1633, 1646, 1660, 1662, 1818, 1960, 2015, 2118, 2171, 2239, 2459, 2469, 2616, 2623, 2624, 2655, 2829, 3114, 3997, 4991, 5588, 5875, 6068, 6091, 6988, 9327, 9328, 9997, 10564, 10775, 11509, 12019, 12738, 12919, 13160, 13418, 13910, 14586, 14615, 14619, 14698, 14908, 14943, 15487, 15502, 15711, 15938, 16167, 16441, 16724, 16973, 16986, 17141, 17240, 17258, 17307, 17395, 17472, 17505, 17779, 17954, 18192, 18513, 19566, 20128, 20925, 21319, 21772, 21774, 21923, 21943, 23059, 23074, 23309, 23352, 23747, 24042, 24526, 25331, 25393, 27212, 27725, 28071, 28251, 29618, 29756, 29792, 30972, 31404, 31863, 34060,
        1275, 2064, 11657, 11780, 16722, 20182, 27498,
        9205, 10429, 15898, 16234, 16985, 20543, 23563,
        1167, 1744, 10160, 10942, 17135, 20056, 21758,
        2493, 2643, 5021, 13703, 14907, 16991, 32358,
        1561, 1976, 2211, 2258, 7490, 20311, 23829,
        1736, 2045, 3037, 5213, 16973, 18231, 33516,
        1766, 1987, 9328, 13160, 16681, 19952, 28449,
        1400, 2240, 3165, 3687, 8913, 14437, 20127,
        6988, 10775, 11062, 13701, 15553, 20058, 24524,
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
