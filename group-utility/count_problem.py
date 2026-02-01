def get_problem_count(problem_list):
    """
    배열을 입력받아 문제의 수(배열의 크기)를 반환하는 함수
    """
    num_problems = len(problem_list)
    return num_problems

# 예시 데이터 (1000, 1001, 1002 형식)
problems = []

# 함수 호출 및 결과 출력
count = get_problem_count(problems)
print(f"현재 배열에 담긴 문제의 수는 '{count}'개입니다.")