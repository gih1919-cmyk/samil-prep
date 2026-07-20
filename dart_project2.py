import requests
import pandas as pd

import os
api_key = os.environ.get("DART_API_KEY")

class Company:
    def __init__(self, name, corp_code):
        self.name = name
        self.corp_code = corp_code
        self.accounts = {} #계정과목들을 담을 딕셔너리??

    def fetch_financials(self, year="2023"):
        url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"
        params = {
            "crtfc_key": api_key,
            "corp_code": self.corp_code,
            "bsns_year": year,
            "reprt_code": "11011",
            "fs_div": "CFS"  # 이 API는 fs_div를 요청 시점에 미리 지정해야한다는디
        }
        response = requests.get(url, params=params)
        data = response.json()
        print(data.get("status"), data.get("message"))

        try:
            for item in data["list"]:
                if item["sj_div"] in ("BS", "IS", "CIS"): # 재무상태표, 손익계산서, 포괄손익계산서만 사용
                    name = item["account_nm"]
                    amount_str = item.get("thstrm_amount", "")
                    if amount_str and name not in self.accounts:
                        amount = int(amount_str.replace(",", ""))
                        self.accounts[name] = amount

        except KeyError as e:
            print(f"{self.name}: KeyError 발생 -", e)
        except ValueError as e:
            print(f"{self.name}: ValueError 발생 -", e)

    def get_debt_ratio(self):
        try:
            debt = self.accounts["부채총계"]
            equity = self.accounts["자본총계"]
            return round(debt / equity * 100, 2)
        except (KeyError, ZeroDivisionError):
            return None

    def get_current_ratio(self):
        try:
            current_assets = self.accounts["유동자산"]
            current_liabilities = self.accounts["유동부채"]
            return round(current_assets / current_liabilities * 100, 2)
        except (KeyError, ZeroDivisionError):
            return None
        
    def get_inventory_turnover(self):
        try:
            revenue = self.accounts.get("매출액") or self.accounts.get("수익(매출액)") or self.accounts.get("영업수익")
            inventory = self.accounts["재고자산"]    
            return round(revenue / inventory, 2)
        except (KeyError, ZeroDivisionError, TypeError):
            return None
test = Company("삼성전자", "00126380")
test.fetch_financials()
for key in test.accounts:
    if "매출" in key or "수익" in key:
        print(key, ":", test.accounts[key])
test = Company("삼성전자", "00126380")
test.fetch_financials()
print("status:", )
print("계정과목 개수:", len(test.accounts))
for key in test.accounts:
    print(key) 

sk = Company("SK하이닉스", "00164779")
sk.fetch_financials()
for key in sk.accounts:
    if "매출" in key or "수익" in key or "재고" in key:
        print(key, ":", sk.accounts[key])     
companies = [
    Company("삼성전자", "00126380"),
    Company("SK하이닉스", "00164779"),
]

results = []
for c in companies:
    c.fetch_financials()
    results.append({
        "기업명": c.name,
        "부채비율(%)": c.get_debt_ratio(),
        "유동비율(%)": c.get_current_ratio(),
        "재고회전율(회)": c.get_inventory_turnover()

    })

df = pd.DataFrame(results)
df.to_excel("재무비율_결과.xlsx", index=False)
print("엑셀 저장 완료!")
print(df)