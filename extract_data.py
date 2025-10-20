import os
import json
import pandas as pd
from bs4 import BeautifulSoup
import re


def extract_number(text):
    """从文本中提取数字"""
    if not text:
        return 0
    # 匹配数字
    numbers = re.findall(r'[\d,]+', text)
    if numbers:
        # 移除逗号并转换为整数
        return int(numbers[0].replace(',', ''))
    return 0


def parse_html_file(file_path):
    """解析HTML文件并提取评论信息"""
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    review_cards = soup.find_all('div', class_='apphub_Card')

    reviews = []

    for card in review_cards:
        try:
            # 提取推荐状态
            thumb_img = card.find('img', src=re.compile(r'icon_thumbs'))
            if thumb_img:
                if 'thumbsUp' in thumb_img['src']:
                    recommendation = '推荐'
                else:
                    recommendation = '不推荐'
            else:
                recommendation = '未知'

            # 提取用户名称
            username_elem = card.select_one('.apphub_CardContentAuthorName a')
            username = username_elem.text.strip() if username_elem else '未知用户'

            # 提取评论内容
            content_elem = card.select_one('.apphub_CardTextContent')
            if content_elem:
                # 移除发布日期元素
                date_elem = content_elem.select_one('.date_posted')
                if date_elem:
                    date_elem.decompose()
                content = content_elem.get_text(strip=True)
            else:
                content = ''

            # 提取发布日期
            date_elem = card.select_one('.date_posted')
            date_posted = date_elem.text.replace('发布于：', '').strip() if date_elem else '未知日期'

            # 提取游戏时长
            hours_elem = card.select_one('.hours')
            hours = hours_elem.text.strip() if hours_elem else '未知时长'

            # 提取有价值人数和欢乐人数
            helpful_elem = card.select_one('.found_helpful')
            helpful_text = helpful_elem.get_text() if helpful_elem else ''

            helpful_count = 0
            funny_count = 0

            if '有' in helpful_text and '人觉得' in helpful_text:
                parts = helpful_text.split('有')
                for part in parts[1:]:
                    if '人觉得这篇评测有价值' in part:
                        helpful_count = extract_number(part.split('人觉得')[0])
                    elif '人觉得这篇评测很欢乐' in part:
                        funny_count = extract_number(part.split('人觉得')[0])

            # 提取奖励数量
            award_elem = card.select_one('.review_award_aggregated')
            award_count = 0
            if award_elem:
                award_text = award_elem.get_text(strip=True)
                # 奖励数量通常是最后一个可见文本
                award_count = extract_number(award_text)

            # 提取评论数量
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
    # 获取用户输入的文件夹名称
    folder_name = input("请输入包含HTML文件的文件夹名称: ").strip()

    if not folder_name:
        print("文件夹名称不能为空!")
        return

    # 检查文件夹是否存在
    if not os.path.exists(folder_name):
        print(f"文件夹 '{folder_name}' 不存在!")
        return

    # 创建输出文件夹
    dataset_folder = f"{folder_name}_dataset"
    dataset_xls_folder = f"{folder_name}_dataset_xls"

    os.makedirs(dataset_folder, exist_ok=True)
    os.makedirs(dataset_xls_folder, exist_ok=True)

    all_reviews = []

    # 遍历文件夹中的所有文件
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

    # 创建DataFrame
    df = pd.DataFrame(all_reviews)

    # 保存到Excel
    excel_filename = f"{folder_name}_dataset.xlsx"
    excel_path = os.path.join(dataset_xls_folder, excel_filename)
    df.to_excel(excel_path, index=False, engine='openpyxl')
    print(f"评论数据已保存到 Excel 文件: {excel_path}")

    # 保存到JSON
    json_filename = f"{folder_name}_dataset_json.json"
    json_path = os.path.join(dataset_folder, json_filename)
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(all_reviews, json_file, ensure_ascii=False, indent=2)
    print(f"评论数据已保存到 JSON 文件: {json_path}")

    # 打印统计信息
    print(f"\n处理完成!")
    print(f"总共提取了 {len(all_reviews)} 条评论")
    print(f"推荐数量: {len([r for r in all_reviews if r['推荐状态'] == '推荐'])}")
    print(f"不推荐数量: {len([r for r in all_reviews if r['推荐状态'] == '不推荐'])}")


if __name__ == "__main__":
    main()