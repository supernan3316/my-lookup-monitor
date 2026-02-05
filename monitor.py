import requests
from bs4 import BeautifulSoup
import os

TARGET_URL = "https://www.megahouse.co.jp/products/lookup/"
SC_SENDKEY = os.environ.get("SC_SENDKEY")
DB_FILE = "history.txt"

def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    print(f"开始访问官网: {TARGET_URL}")
    
    try:
        res = requests.get(TARGET_URL, headers=headers, timeout=30)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 尝试抓取标题
        items = soup.select('.pr_card_ttl') or soup.select('.item_name')
        current_products = [item.get_text(strip=True) for item in items if item.get_text(strip=True)]
        
        print(f"成功抓取到 {len(current_products)} 个商品")

       

        # --- 原有的逻辑：发现新品才推送详细名单 ---
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                history = {line.strip() for line in f if line.strip()}
        else:
            history = set()

        new_items = set(current_products) - history
        if new_items:
            content = "发现新品：\n" + "\n".join(new_items)
            requests.post(f"https://sctapi.ftqq.com/{SC_SENDKEY}.send", 
                          data={"title": "るかっぷ新品提醒!", "desp": content})
            
            with open(DB_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(current_products))
                
    except Exception as e:
        error_info = f"运行出错: {str(e)}"
        print(error_info)
        requests.post(f"https://sctapi.ftqq.com/{SC_SENDKEY}.send", 
                      data={"title": "监控脚本报错", "desp": error_info})

if __name__ == "__main__":
    main()
