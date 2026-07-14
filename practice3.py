import requests

response = requests.get("https://jsonplaceholder.typicode.com/users/1")
data = response.json()

print(data)
print("이름", data["name"])
print("이메일", data["email"])