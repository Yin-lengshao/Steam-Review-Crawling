import os
import json
import pandas as pd
from bs4 import BeautifulSoup
import re


def extract_number(text):
    if not text:
        return 0
    numbers = re.findall(r'[\d,]+', text)
    if numbers:
        return int(numbers[0].replace(',', ''))
    return 0

def parse_html_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    review_cards = soup.find_all('div', class_='apphub_Card')
    reviews = []
    for card in review_cards:
        try:
            thumb_img = card.find('img', src=re.compile(r'icon_thumbs'))
            if thumb_img:
                if 'thumbsUp' in thumb_img['src']:
                    recommendation = '推荐'
                else:
                    recommendation = '不推荐'
            else:
                recommendation = '未知'
            username_elem = card.select_one('.apphub_CardContentAuthorName a')
            username = username_elem.text.strip() if username_elem else '未知用户'
            content_elem = card.select_one('.apphub_CardTextContent')
            content = ''
            date_posted = '未知日期'
            if content_elem:
                date_elem = content_elem.find('div', class_='date_posted')
                if date_elem:
                    date_posted = date_elem.get_text(strip=True).replace('发布于：', '')
                    date_elem.decompose()
                content = content_elem.get_text(strip=True)
            hours_elem = card.select_one('.hours')
            hours = hours_elem.text.strip() if hours_elem else '未知时长'
            helpful_elem = card.select_one('.found_helpful')
            helpful_text = helpful_elem.get_text() if helpful_elem else ''
            helpful_count = 0
            funny_count = 0
            if '有' in helpful_text and '人觉得' in helpful_text:
                helpful_match = re.search(r'有\s*(\d+)\s*人觉得这篇评测有价值', helpful_text)
                if helpful_match:
                    helpful_count = int(helpful_match.group(1))
                funny_match = re.search(r'有\s*(\d+)\s*人觉得这篇评测很欢乐', helpful_text)
                if funny_match:
                    funny_count = int(funny_match.group(1))
            award_elem = card.select_one('.review_award_aggregated')
            award_count = 0
            if award_elem:
                award_text = award_elem.get_text(strip=True)
                award_count = extract_number(award_text)
            comment_elem = card.select_one('.apphub_CardCommentCount')
            comment_count = extract_number(comment_elem.text) if comment_elem else 0
            review_data = {
                '推荐状态': recommendation,
                '用户名称': username,
                '评论内容': content,
                '发布日期': date_posted,
                '游戏时长': hours,
                '有价值人数': helpful_count,
                '欢乐人数': funny_count,
                '奖励数量': award_count,
                '评论数量': comment_count
            }
            reviews.append(review_data)
        except Exception as e:
            print(f"解析评论时出错: {e}")
            continue
    return reviews


def main():
    folder_name = input("请输入包含HTML文件的文件夹名称: ").strip()
    if not folder_name:
        print("文件夹名称不能为空!")
        return
    if not os.path.exists(folder_name):
        print(f"文件夹 '{folder_name}' 不存在!")
        return
    dataset_folder = f"{folder_name}_dataset"
    dataset_xls_folder = f"{folder_name}_dataset_xls"
    os.makedirs(dataset_folder, exist_ok=True)
    os.makedirs(dataset_xls_folder, exist_ok=True)
    all_reviews = []
    for filename in os.listdir(folder_name):
        if filename.startswith('page_'):
            file_path = os.path.join(folder_name, filename)
            if os.path.isfile(file_path):
                print(f"正在处理文件: {filename}")
                reviews = parse_html_file(file_path)
                all_reviews.extend(reviews)
                print(f"从 {filename} 中提取了 {len(reviews)} 条评论")
    if not all_reviews:
        print("未找到任何评论数据!")
        return
    df = pd.DataFrame(all_reviews)
    excel_filename = f"{folder_name}_dataset.xlsx"
    excel_path = os.path.join(dataset_xls_folder, excel_filename)
    df.to_excel(excel_path, index=False, engine='openpyxl')
    print(f"评论数据已保存到 Excel 文件: {excel_path}")
    json_filename = f"{folder_name}_dataset_json.json"
    json_path = os.path.join(dataset_folder, json_filename)
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(all_reviews, json_file, ensure_ascii=False, indent=2)
    print(f"评论数据已保存到 JSON 文件: {json_path}")
    print(f"\n处理完成!")
    print(f"总共提取了 {len(all_reviews)} 条评论")
    print(f"推荐数量: {len([r for r in all_reviews if r['推荐状态'] == '推荐'])}")
    print(f"不推荐数量: {len([r for r in all_reviews if r['推荐状态'] == '不推荐'])}")


if __name__ == "__main__":
    main()