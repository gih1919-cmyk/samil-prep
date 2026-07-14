import pandas as pd

companies = [ 
    {"기업명": "A사", "부채": 500, "자본": 250},
    {"기업명": "B사", "부채": 300, "자본": 400},
    {"기업명": "C사", "부채": 700, "자본": 100},
]

df = pd.DataFrame(companies)

print(df)

df["부채비율"] = df["부채"] / df["자본"] * 100
print(df)

df.to_excel("부채비율_결과.xlsx", index=False)
print("엑셀 저장 완료 !!!!!")
