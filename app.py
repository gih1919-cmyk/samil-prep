import xml.etree.ElementTree as ET

def find_corp_code(company_name):
    tree = ET.parse("CORPCODE.xml")
    root = tree.getroot()
    for company in root.findall("list"):
        name = company.find("corp_name").text
        if name == company_name:
            return company.find("corp_code").text
    return None

from flask import Flask
import requests
import pandas as pd
import os

app = Flask(__name__)
api_key = os.environ.get("DART_API_KEY")

class Company:
    def __init__(self, name, corp_code):
        self.name = name
        self.corp_code = corp_code
        self.accounts = {}

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
            "fs_div": "CFS"
        }
        response = requests.get(url, params=params)
        data = response.json()

        try:
            for item in data["list"]:
                if item["sj_div"] in ("BS", "IS", "CIS"):
                    name = item["account_nm"]
                    amount_str = item.get("thstrm_amount", "")
                    if amount_str and name not in self.accounts:
                        self.accounts[name] = int(amount_str.replace(",", ""))
        except KeyError as e:
            print(f"{self.name}: KeyError 발생 -", e)
        except ValueError as e:
            print(f"{self.name}: ValueError 발생 -", e)

    def get_debt_ratio(self):
        try:
            return round(self.get_account("부채총계") / self.get_account("자본총계") * 100, 2)
        except (TypeError, ZeroDivisionError):
            return None

    def get_current_ratio(self):
        try:
            return round(self.get_account("유동자산") / self.get_account("유동부채") * 100, 2)
        except (TypeError, ZeroDivisionError):
            return None

    def get_operating_margin(self):
        try:
            operating_income = self.get_account("영업이익", "영업이익(손실)", "영업손실")
            revenue = self.get_account("매출액", "수익(매출액)", "영업수익")
            return round(operating_income / revenue * 100, 2)
        except (TypeError, ZeroDivisionError):
            return None

    def get_net_margin(self):
        try:
            net_income = self.get_account("당기순이익(손실)", "당기순이익", "당기순손실", "지배기업의 소유주에게 귀속되는 당기순이익(손실)")
            revenue = self.get_account("매출액", "수익(매출액)", "영업수익")
            return round(net_income / revenue * 100, 2)
        except (TypeError, ZeroDivisionError):
            return None

    def get_roa(self):
        try:
            net_income = self.get_account("당기순이익(손실)", "당기순이익", "당기순손실", "지배기업의 소유주에게 귀속되는 당기순이익(손실)")
            total_assets = self.get_account("자산총계")
            return round(net_income / total_assets * 100, 2)
        except (TypeError, ZeroDivisionError):
            return None

    def get_roe(self):
        try:
            net_income = self.get_account("당기순이익(손실)", "당기순이익", "당기순손실", "지배기업의 소유주에게 귀속되는 당기순이익(손실)")
            equity = self.get_account("자본총계")
            return round(net_income / equity * 100, 2)
        except (TypeError, ZeroDivisionError):
            return None

    def get_inventory_turnover(self):
        try:
            revenue = self.get_account("매출액", "수익(매출액)", "영업수익")
            inventory = self.get_account("재고자산")
            return round(revenue / inventory, 2)
        except (TypeError, ZeroDivisionError):
            return None



from flask import request

@app.route("/")
def home():
    search_query = request.args.get("company")  # 검색창에 입력한 값 받기

    companies = [
        Company("삼성전자", "00126380"),
        Company("SK하이닉스", "00164779"),
        Company("야놀자", "00907864"),
    ]

    if search_query:
        corp_code = find_corp_code(search_query)
        if corp_code:
            companies.append(Company(search_query, corp_code))

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
    table_html = df.to_html(index=False, classes="ratio-table", border=0)

    search_box = '''
    <form action="/" method="get">
        <input type="text" name="company" placeholder="기업명 검색 (예: LG전자)">
        <button type="submit">검색</button>
    </form>
    '''

    page = f"""
    <html>
    <head>
        <title>재무비율 대시보드</title>
        <style>
            body {{ font-family: 'Malgun Gothic', sans-serif; background-color: #f4f6f8; padding: 40px; }}
            h1 {{ color: #2c3e50; }}
            form {{ margin: 20px 0; }}
            input {{ padding: 8px; width: 200px; }}
            button {{ padding: 8px 16px; background-color: #2c3e50; color: white; border: none; cursor: pointer; }}
            .ratio-table {{ border-collapse: collapse; width: 100%; background-color: white; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }}
            .ratio-table th {{ background-color: #2c3e50; color: white; padding: 12px; text-align: center; }}
            .ratio-table td {{ padding: 10px; text-align: center; border-bottom: 1px solid #eee; }}
            .download-btn {{ display: inline-block; margin-top: 20px; padding: 10px 20px; background-color: #27ae60; color: white; text-decoration: none; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>📊 기업 재무비율 대시보드</h1>
        <p>DART Open API 기반 자동 계산 결과입니다.</p>
        {search_box}
        {table_html}
        <a href="/download" class="download-btn">📥 엑셀로 다운로드</a>
    </body>
    </html>
    """
    return page

from flask import send_file
import io

@app.route("/download")
def download():
    companies = [
        Company("삼성전자", "00126380"),
        Company("SK하이닉스", "00164779"),
        Company("야놀자", "00907864"),
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

    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    return send_file(
        output,
        download_name="재무비율_결과.xlsx",
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)