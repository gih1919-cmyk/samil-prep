import requests
import pandas as pd

api_key = "a4f83869d58d26298663d6cce0073e9c2116ef28"

class Company:
    def __init__(self, name, corp_code):
        self.name = name
        self.corp_code = corp_code
        self.debt_total = None
        self.equity_total = None

    def fetch_financials(self, year="2023"):
        url = "https://opendart.fss.or.kr/api/fnlttSinglAcnt.json"
        params = {
            "crtfc_key": api_key,
            "corp_code": self.corp_code,
            "bsns_year": year,
            "reprt_code": "11011"
        }
        response = requests.get(url, params=params)
        data = response.json()

        try:
            for item in data["list"]:
                if item["fs_div"] == "CFS" and item["account_nm"] == "부채총계":
                    self.debt_total = int(item["thstrm_amount"].replace(",", ""))
                if item["fs_div"] == "CFS" and item["account_nm"] == "자본총계":
                    self.equity_total = int(item["thstrm_amount"].replace(",", ""))
        except KeyError:
            print(f"{self.name}: 데이터 조회 실패")

    def get_debt_ratio(self):
        try:
            return round(self.debt_total / self.equity_total * 100, 2)
        except (TypeError, ZeroDivisionError):
            return None
        
companies = [
    Company("삼성전자", "00126380"),
    Company("SK하이닉스", "00164779"),
]

results = []
for c in companies:
    c.fetch_financials()
    results.append({
        "기업명": c.name,
        "부채총계": c.debt_total,
        "자본총계": c.equity_total,
        "부채비율(%)": c.get_debt_ratio()
    })

df = pd.DataFrame(results)
df.to_excel("부채비율_결과.xlsx", index=False)
print("엑셀 저장 완료!")
print(df)