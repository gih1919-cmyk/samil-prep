class Company:
    def __init__(self, name, debt, equity):
        self.name = name
        self.debt = debt
        self.equity = equity
    
    def get_debt_ratio(self):
        try:
            return self.debt / self.equity * 100
        except ZeroDivisionError:
            return None #자본이 0이면 계산불가
a_company = Company("A사", 500, 250)
b_company = Company("B사", 300, 0) # 자본0 테스트

print(a_company.name, a_company.get_debt_ratio())
print(b_company.name, b_company.get_debt_ratio())
