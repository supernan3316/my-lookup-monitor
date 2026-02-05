import requests
from bs4 import BeautifulSoup
import os

# 目标网址
TARGET_URL = "https://www.megahouse.co.jp/products/lookup/"
SC_SENDKEY = os.environ.get("SC_SENDKEY")
DB_FILE = "history.txt"

def main():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        # 获取网页内容
        res = requests.get(TARGET_URL, headers=headers)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 抓取所有商品名称
        items = soup.select('.pr_card_ttl') or soup.find_all("p", class_="item_name")
        current_products = {item.get_text(strip=True) for item in items if item.get_text(strip=True)}

        # 读取旧纪录
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                history = {line.strip() for line in f if line.strip()}
        else:
            history = set()

        # 发现新周边
        new_items = current_products - history

        if new_items:
            print(f"发现新商品: {new_items}")
            content = "\n".join(new_items)
            # 发送到微信
            requests.post(f"https://sctapi.ftqq.com/{SC_SENDKEY}.send", 
                          data={"title": "るかっぷ(LookUp)出新品啦！", "desp": content})
            # 更新历史记录
            with open(DB_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(current_products))
        else:
            print("没有新发现。")
            
    except Exception as e:
        print(f"运行出错: {e}")

if __name__ == "__main__":
    main()
