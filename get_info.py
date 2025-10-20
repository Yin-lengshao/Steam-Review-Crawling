import requests
from urllib.parse import urlencode
import time
import os
import urllib3
import random

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def crawl_steam_reviews(start_url, num_pages, save_dir="html_pages"):
    # 创建session并禁用SSL验证
    session = requests.Session()
    session.verify = False  # 禁用SSL验证
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    # 创建保存目录
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    current_url = start_url
    saved_files = []

    # 简单计数，从1开始
    page_counter = 1

    for i in range(num_pages):
        print(f"正在获取第 {page_counter} 页...")

        try:
            # 发送请求
            response = session.get(current_url, timeout=30)
            response.raise_for_status()

            # 保存HTML - 使用简单的计数器
            filename = f"page_{page_counter}.html"
            filepath = os.path.join(save_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)

            saved_files.append(filepath)
            print(f"✓ 第 {page_counter} 页已保存: {filepath}")

            # 如果是最后一页，提前结束
            if i == num_pages - 1:
                break

            # 从HTML中提取下一页游标
            next_url = extract_next_url(response.text, current_url)
            if not next_url:
                print("没有找到下一页，爬取结束")
                break

            current_url = next_url
            page_counter += 1  # 增加计数器

            # 延迟
            time.sleep(random.randint(1,3))

        except requests.exceptions.SSLError as e:
            print(f"SSL错误: {e}")
            print("尝试使用更宽松的SSL配置...")
            session.verify = False
            continue
        except requests.exceptions.RequestException as e:
            print(f"请求第 {page_counter} 页时出错: {e}")
            break
        except Exception as e:
            print(f"处理第 {page_counter} 页时出错: {e}")
            break

    return saved_files


def extract_next_url(html_content, current_url):
    """从HTML内容中提取下一页URL"""
    try:
        # 查找分页游标
        cursor_start = html_content.find('name="userreviewscursor" value="')
        if cursor_start == -1:
            return None

        cursor_start += len('name="userreviewscursor" value="')
        cursor_end = html_content.find('"', cursor_start)
        next_cursor = html_content[cursor_start:cursor_end]

        # 从当前URL提取参数
        from urllib.parse import parse_qs, urlparse
        parsed = urlparse(current_url)
        params = parse_qs(parsed.query)

        # 递增参数
        current_page = int(params.get('p', [1])[0])
        current_offset = int(params.get('userreviewsoffset', [0])[0])

        next_page = current_page + 1
        next_offset = current_offset + 10

        # 构建新参数
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

        # 生成URL
        query_string = urlencode(new_params)
        base_url = current_url.split('?')[0]
        next_url = base_url + '?' + query_string

        return next_url

    except Exception as e:
        print(f"提取下一页URL时出错: {e}")
        return None


# 使用示例
if __name__ == "__main__":
    # 初始URL
    start_url = input("输入起始url：")

    # 用户输入
    try:
        num_pages = int(input("请输入要爬取的页数: "))
    except ValueError:
        num_pages = 3  # 默认值

    save_dir = input("请输入保存目录（默认: html_pages）: ").strip()
    if not save_dir:
        save_dir = "html_pages"

    # 开始爬取
    print(f"开始爬取 {num_pages} 页HTML内容...")
    saved_files = crawl_steam_reviews(start_url, num_pages, save_dir)

    # 输出结果
    print(f"\n爬取完成！共保存 {len(saved_files)} 个HTML文件:")
    for filepath in saved_files:
        print(f"  - {filepath}")