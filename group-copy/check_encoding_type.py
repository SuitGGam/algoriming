import chardet

with open('problemworkbooks_all_pages_edit.csv', 'rb') as f:
    rawdata = f.read(10000)  # 샘플 읽기
    result = chardet.detect(rawdata)
    print(result)
