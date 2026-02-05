import requests
from bs4 import BeautifulSoup
import os

# 配置 Server酱 SendKey
SC_SENDKEY = os.environ.get('SC_SENDKEY')

def fetch_lookup_products():
    url = "https://www.megahouse.co.jp/products/lookup/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
    }
    
    print(f"开始访问官网: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"访问失败，状态码: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        products = []

        # 策略 1: 寻找所有可能的商品标题 class
        items = soup.find_all(['p', 'h3', 'div'], class_=['m-productsList_itemTitle', 'title', 'name'])
        
        # 策略 2: 如果策略 1 没抓到，直接抓取带有 products/item 链接的文字
        if not items:
            links = soup.find_all('a', href=True)
            for link in links:
                if '/products/item/' in link['href']:
                    name = link.get_text().strip()
                    if name:
                        products.append(name)
        else:
            for item in items:
                name = item.get_text().strip()
                if name:
                    products.append(name)
        
        # 去重
        products = list(set(products))
        print(f"成功抓取到 {len(products)} 个商品")
        return products
    except Exception as e:
        print(f"发生错误: {e}")
        return []

def main():
    current_products = fetch_lookup_products()
    
    # 如果实在抓不到，为了调试，我们打印出网页的前 500 个字符看看
    if not current_products:
        print("警告：未抓取到任何商品。请检查官网是否改版。")
        return

    history_file = 'history.txt'
    
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            old_products = [line.strip() for line in f.readlines()]
    else:
        old_products = []

    new_products = [p for p in current_products if p not in old_products]

    if new_products:
        print(f"发现新品: {len(new_products)} 个")
        # 限制推送长度，防止消息过长
        msg_content = "\n".join(new_products[:20]) 
        requests.post(f"https://sctapi.ftqq.com/{SC_SENDKEY}.send", 
                      data={"title": f"るかっぷ官网更新({len(new_products)}件)", "desp": msg_content})
    else:
        print("没有发现新品")

    # 只要抓到了东西，就强制更新 history.txt
    with open(history_file, 'w', encoding='utf-8') as f:
        for p in current_products:
            f.write(f"{p}\n")

if __name__ == "__main__":
    main()
