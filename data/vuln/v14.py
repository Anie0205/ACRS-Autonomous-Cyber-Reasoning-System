import requests
url = input()
print(requests.get(url).text)
