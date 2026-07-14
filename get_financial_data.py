import requests
api_key = 	"a4f83869d58d26298663d6cce0073e9c2116ef28"
corp_code = "00126380"

url = "https://opendart.fss.or.kr/api/fnlttSinglAcnt.json"
params = {
    "crtfc_key": api_key,
    "corp_code": corp_code,
    "bsns_year": "2023",
    "reprt_code": "11011"
}

response = requests.get(url, params=params)
data = response.json()

print(data)

#연결재무제표 기준으로 부채총계, 자본총계 찾기
debt_total = None
equity_total = None

for item in data["list"]:
    if item["fs_div"] == "CFS" and item["account_nm"] == "부채총계":
        debt_total = int(item["thstrm_amount"].replace(",", ""))
    if item["fs_div"] == "CFS" and item["account_nm"] == "자본총계":
        equity_total = int(item["thstrm_amount"].replace(",", ""))

debt_ratio = debt_total / equity_total * 100
print(f"부채총계: {debt_total:,}원")
print(f"자본총계: {equity_total:,}원")
print(f"부채비율: {debt_ratio:.2f}%")

import pandas as pd

result = [ 
    {"기업명": "삼성전자", "부채총계": debt_total, "자본총계": equity_total, "부채비율(%)": round(debt_ratio, 2)}]

df = pd.DataFrame(result)
df.to_excel("부채비율_결과.xlsx", index=False)
print("엑셀 저장 완료!!")