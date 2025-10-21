import requests
from urllib.parse import urlencode
import time
import os
import urllib3
import random
from fake_useragent import UserAgent

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def crawl_steam_reviews(start_url, num_pages, save_dir="html_pages"):
    ua = UserAgent()

    session = requests.Session()
    session.verify = False

    session.headers.update({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
    })

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    current_url = start_url
    saved_files = []
    page_counter = 1

    for i in range(num_pages):
        print(f"正在获取第 {page_counter} 页...")

        # 每次请求前更新 User-Agent
        session.headers['User-Agent'] = ua.random

        # 随机延迟，模拟人类行为
        delay = random.uniform(2, 5)
        time.sleep(delay)

        max_retries = 3
        for retry in range(max_retries):
            try:
                response = session.get(current_url, timeout=30)
                response.raise_for_status()

                # 检查是否被反爬（比如返回了错误页面）
                if check_anti_crawler(response.text):
                    print(f"检测到反爬机制，等待后重试... (第{retry + 1}次)")
                    time.sleep(random.uniform(10, 20))
                    continue

                filename = f"page_{page_counter}.html"
                filepath = os.path.join(save_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                saved_files.append(filepath)
                print(f"✓ 第 {page_counter} 页已保存: {filepath}")

                if i == num_pages - 1:
                    break

                next_url = extract_next_url(response.text, current_url)
                if not next_url:
                    print("没有找到下一页，爬取结束")
                    break

                current_url = next_url
                page_counter += 1
                break

            except requests.exceptions.SSLError as e:
                print(f"SSL错误: {e}")
                print("尝试使用更宽松的SSL配置...")
                session.verify = False
                continue
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:  # 请求过多
                    wait_time = random.uniform(30, 60)
                    print(f"请求过于频繁，等待 {wait_time:.1f} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                elif response.status_code in [403, 503]:  # 禁止访问或服务不可用
                    wait_time = random.uniform(20, 40)
                    print(f"遇到 {response.status_code} 错误，等待 {wait_time:.1f} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"HTTP错误 {response.status_code}: {e}")
                    if retry == max_retries - 1:
                        raise
            except requests.exceptions.Timeout:
                print(f"请求超时，第 {retry + 1} 次重试...")
                if retry == max_retries - 1:
                    raise
            except requests.exceptions.RequestException as e:
                print(f"请求第 {page_counter} 页时出错: {e}")
                if retry == max_retries - 1:
                    break
            except Exception as e:
                print(f"处理第 {page_counter} 页时出错: {e}")
                if retry == max_retries - 1:
                    break

            if retry < max_retries - 1:
                wait_time = random.uniform(10, 30)
                print(f"等待 {wait_time:.1f} 秒后重试...")
                time.sleep(wait_time)
        else:
            print(f"第 {page_counter} 页经过 {max_retries} 次重试后仍然失败，跳过...")
            continue

    return saved_files


def check_anti_crawler(html_content):
    anti_crawler_indicators = [
        "access denied",
        "robot check",
        "captcha",
        "cloudflare",
        "too many requests",
        "rate limit",
        "bot detected"
    ]

    content_lower = html_content.lower()
    for indicator in anti_crawler_indicators:
        if indicator in content_lower:
            return True
    if len(html_content) < 1000:
        return True

    return False


def extract_next_url(html_content, current_url):
    try:
        cursor_start = html_content.find('name="userreviewscursor" value="')
        if cursor_start == -1:
            return None

        cursor_start += len('name="userreviewscursor" value="')
        cursor_end = html_content.find('"', cursor_start)
        next_cursor = html_content[cursor_start:cursor_end]

        from urllib.parse import parse_qs, urlparse
        parsed = urlparse(current_url)
        params = parse_qs(parsed.query)

        current_page = int(params.get('p', [1])[0])
        current_offset = int(params.get('userreviewsoffset', [0])[0])

        next_page = current_page + 1
        next_offset = current_offset + 10

        new_params = {
            'userreviewscursor': next_cursor,
            'userreviewsoffset': str(next_offset),
            'p': str(next_page),
            'workshopitemspage': str(next_page),
            'readytouseitemspage': str(next_page),
            'mtxitemspage': str(next_page),
            'itemspage': str(next_page),
            'screenshotspage': str(next_page),
            'videospage': str(next_page),
            'artpage': str(next_page),
            'allguidepage': str(next_page),
            'webguidepage': str(next_page),
            'integratedguidepage': str(next_page),
            'discussionspage': str(next_page),
            'numperpage': '10',
            'browsefilter': 'toprated',
            'appid': params.get('appid', ['2807960'])[0],
            'appHubSubSection': '10',
            'l': 'schinese',
            'filterLanguage': 'default',
            'searchText': '',
            'maxInappropriateScore': '100',
            'forceanon': '1'
        }

        query_string = urlencode(new_params)
        base_url = current_url.split('?')[0]
        next_url = base_url + '?' + query_string

        return next_url

    except Exception as e:
        print(f"提取下一页URL时出错: {e}")
        return None


if __name__ == "__main__":
    start_url = input("输入起始url：")
    try:
        num_pages = int(input("请输入要爬取的页数: "))
    except ValueError:
        num_pages = 3
    save_dir = input("请输入保存目录（默认: html_pages）: ").strip()
    if not save_dir:
        save_dir = "html_pages"

    print(f"开始爬取 {num_pages} 页HTML内容...")
    saved_files = crawl_steam_reviews(start_url, num_pages, save_dir)
    print(f"\n爬取完成！共保存 {len(saved_files)} 个HTML文件:")
    for filepath in saved_files:

        print(f"  - {filepath}")
