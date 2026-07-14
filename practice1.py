# 리스트 컴프리헨션 연습
numbers = list(range(1, 11))
evens = [n for n in numbers if n % 2 == 0]
print("짝수만:", evens)

squares = [n**2 for n in numbers]
print("제곱:", squares)