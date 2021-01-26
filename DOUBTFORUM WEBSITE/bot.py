import json,requests

url = 'https://api.telegram.org/bot1189449234:AAGz1eDsZQ7ACjDhXMv2MMINocihpaI6z8A/getupdates'
r = requests.get(url=url)
print(r.text)
data = r.text
parsed = json.loads(data)
print(parsed)
with open('bot.json', "x") as c:
    params = json.load(c)[r.text]
    print(params)