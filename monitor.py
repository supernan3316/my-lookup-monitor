import requests
from bs4 import BeautifulSoup
import os

TARGET_URL = "https://www.megahouse.co.jp/products/lookup/"
SC_SENDKEY = os.environ.get("SC_SENDKEY")
DB_FILE = "history.txt"

def main():
    # 模拟真实浏览器，防止被拦截
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1"
    }
    try:
        res = requests.get(TARGET_URL, headers=headers, timeout=30)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 尝试多种方式抓取标题
        items = soup.select('.pr_card_ttl') or soup.select('.item_name')
        current_products = {item.get_text(strip=True) for item in items if item.get_text(strip=True)}
        
        print(f"当前抓取到 {len(current_products)} 个商品")

        if not current_products:
            print("警告：未能抓取到任何商品，请检查网页结构")
            return

        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                history = {line.strip() for line in f if line.strip()}
        else:
            history = set()

        new_items = current_products - history

        if new_items:
            content = "\n".join(new_items)
            # 发送消息并打印结果
            push_res = requests.post(f"https://sctapi.ftqq.com/{SC_SENDKEY}.send", 
                                     data={"title": "LookUp新品提醒!", "desp": content})
            print(f"推送结果: {push_res.text}")
            
            with open(DB_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(current_products))
        else:
            print("没有新发现。")
            
    except Exception as e:
        print(f"运行出错: {e}")

if __name__ == "__main__":
    main()
