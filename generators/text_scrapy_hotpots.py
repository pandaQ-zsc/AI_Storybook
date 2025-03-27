# 使用Python自动化热点抓取（示例代码）
import requests
from bs4 import BeautifulSoup

def get_buzzsumo_data(keyword):
    url = f"https://api.buzzsumo.com/search?q={keyword}&type=articles"
    headers = {"Authorization": "Bearer YOUR_API_KEY"}
    response = requests.get(url, headers=headers)
    data = response.json()
    top_titles = [item['title'] for item in data['results'][:5]]
    return top_titles

if __name__ == "__main__":
    # 执行抓取
    hot_topics = get_buzzsumo_data("职场技能")
    print(f"当日爆款选题：{hot_topics}")
