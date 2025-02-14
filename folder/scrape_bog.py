import requests
from bs4 import BeautifulSoup
import os

def scrape_blog_to_md(url, filename):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"블로그 페이지를 가져오는 데 실패했습니다. 상태 코드: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('title').get_text()
    content = soup.find('div', class_='tt_article_useless_p_margin contents_style')

    if content is None:
        print("기사 내용을 찾을 수 없습니다.")
        return

    filepath = f"/home/kang/문서/bolg_scrap/article/{filename}"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(content.get_text(strip=True, separator='\n'))

def get_blog_number():
    num_file_path = "blog_number.txt"

    if not os.path.exists(num_file_path):
        with open(num_file_path, 'w') as f:
            f.write("1")
        return 1

    with open(num_file_path, 'r') as f:
        current_number = int(f.read().strip())

    return current_number

def save_blog_number(number):
    with open("blog_number.txt", 'w') as f:
        f.write(str(number))

if __name__ == "__main__":
    # 블로그 번호 가져오기
    blog_no = get_blog_number()
    url = f"https://cs-study1.tistory.com/{blog_no}"
    filename = f"blog_post_{blog_no}.md"

    # 스크랩 실행
    scrape_blog_to_md(url, filename)
    print(f"{filename}에 블로그 내용이 저장되었습니다.")

    # 블로그 번호 증가
    blog_no += 1
    save_blog_number(blog_no)

    print(f"다음 블로그 번호: {blog_no}.")
