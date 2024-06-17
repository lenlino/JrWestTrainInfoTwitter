import requests
from bs4 import BeautifulSoup

# HTMLの取得(GET)
req = requests.get("https://trafficinfo.westjr.co.jp/kinki.html")
req.encoding = req.apparent_encoding # 日本語の文字化け防止

# HTMLの解析
bsObj = BeautifulSoup(req.text,"html.parser")

map = bsObj.find(class_="map")
map = map.find("img")
print(map)

items = bsObj.find(id="syosai_4").find_all(class_="jisyo_contents")

for item in items:
    contents = item.find_all("p")
    for content in contents:
        print(content.text)


