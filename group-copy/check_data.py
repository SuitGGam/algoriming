import pandas as pd

df = pd.read_csv('problemworkbooks_all_pages_edit.csv', encoding='utf-8-sig')
print(len(df))   # 행 개수 출력(헤더 제외)
print(df.tail()) # 마지막 5개 행 내용 확인
