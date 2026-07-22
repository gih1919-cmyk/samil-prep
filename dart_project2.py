import requests
import pandas as pd

api_key = "a4f83869d58d26298663d6cce0073e9c2116ef28"

class Company:
    def __init__(self, name, corp_code):
        self.name = name
        self.corp_code = corp_code
        self.accounts = {} #계정과목들을 담을 딕셔너리??

    def get_account(self, *names):
        for n in names:
            if n in self.accounts:
                return self.accounts[n]
        return None
    
    def fetch_financials(self, year="2025"):
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
                if item["sj_div"] in ("BS", "IS", "CIS"): # 재무상태표, 손익계산서만 사용
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
    
    def get_operating_margin(self):  # 영업이익률
        try:
            operating_income = self.get_account("영업이익", "영업이익(손실)", "영업손실")
            revenue = self.get_account("매출액", "수익(매출액)", "영업수익")
            return round(operating_income / revenue * 100, 2)
        except (TypeError, ZeroDivisionError):
            return None

    def get_net_margin(self):  # 순이익률
        try:
            net_income = self.get_account("당기순이익(손실)", "당기순이익", "당기순손실", "지배기업의 소유주에게 귀속되는 당기순이익(손실)")
            revenue = self.get_account("매출액", "수익(매출액)", "영업수익")
            return round(net_income / revenue * 100, 2)
        except (TypeError, ZeroDivisionError):
            return None

    def get_roa(self):  # 총자산이익률
        try:
            net_income = self.get_account("당기순이익(손실)", "당기순이익", "당기순손실", "지배기업의 소유주에게 귀속되는 당기순이익(손실)")
            total_assets = self.get_account("자산총계")
            return round(net_income / total_assets * 100, 2)
        except (TypeError, ZeroDivisionError):
            return None

    def get_roe(self):  # 자기자본이익률
        try:
            net_income = self.get_account("당기순이익(손실)", "당기순이익", "당기순손실", "지배기업의 소유주에게 귀속되는 당기순이익(손실)")
            equity = self.get_account("자본총계")
            return round(net_income / equity * 100, 2)
        except (TypeError, ZeroDivisionError):
            return None
        
    def get_inventory_turnover(self):
        try:
            revenue = self.accounts.get("매출액") or self.accounts.get("수익(매출액)") or self.accounts.get("영업수익")    # 어떤 계정과목이 필요할까요?
            inventory = self.accounts["재고자산"]     
            return round(revenue / inventory, 2)
        except (KeyError, ZeroDivisionError, TypeError):
            return None
            
test = Company("삼성전자", "00126380")
test.fetch_financials()
for key in test.accounts:
    if "매출" in key or "수익" in key:
        print(key, ":", test.accounts[key])
for key in test.accounts:
    if "순이익" in key:
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
    Company("야놀자", "00907864")
]

results = []
for c in companies:
    c.fetch_financials()
    results.append({
        "기업명": c.name,
        "부채비율(%)": c.get_debt_ratio(),
        "유동비율(%)": c.get_current_ratio(),
        "재고회전율(회)": c.get_inventory_turnover(),
        "영업이익률(%)": c.get_operating_margin(),
        "순이익률(%)": c.get_net_margin(),
        "ROA(%)": c.get_roa(),
        "ROE(%)": c.get_roe(),
    })

df = pd.DataFrame(results)
df.to_excel("재무비율_결과.xlsx", index=False)
print("엑셀 저장 완료!")
print(df)

