import requests
from bs4 import BeautifulSoup
import os

# 配置 Server酱 SendKey
SC_SENDKEY = os.environ.get('SC_SENDKEY')

def fetch_lookup_products():
    url = "https://www.megahouse.co.jp/products/lookup/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print(f"开始访问官网: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"访问失败，状态码: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 修正爬取逻辑：根据官网最新的 class 结构抓取
        products = []
        # 尝试抓取所有的商品标题
        items = soup.select('.m-productsList_itemTitle') or soup.select('p.title')
        
        for item in items:
            name = item.get_text().strip()
            if name:
                products.append(name)
        
        print(f"成功抓取到 {len(products)} 个商品")
        return products
    except Exception as e:
        print(f"发生错误: {e}")
        return []

def main():
    current_products = fetch_lookup_products()
    
    if not current_products:
        print("未抓取到商品，跳过本次运行。")
        return

    history_file = 'history.txt'
    
    # 读取历史记录
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            old_products = [line.strip() for line in f.readlines()]
    else:
        old_products = []

    # 找出新品
    new_products = [p for p in current_products if p not in old_products]

    if new_products:
        print(f"发现新品: {new_products}")
        msg = "\n".join(new_products)
        # 发送推送
        requests.post(f"https://sctapi.ftqq.com/{SC_SENDKEY}.send", 
                      data={"title": "るかっぷ官网有更新！", "desp": msg})
    else:
        print("没有发现新品")

    # 无论是否有新品，都更新一次 history.txt 以保证文件存在
    with open(history_file, 'w', encoding='utf-8') as f:
        for p in current_products:
            f.write(f"{p}\n")

if __name__ == "__main__":
    main()
