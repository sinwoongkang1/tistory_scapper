# [블로그 포스팅 Auto Push] 로컬 PC

블로그에 포스팅 된 내용을 자동으로 스크랩 하여 특정 저장소에 [포스팅제목].md 파일을 생성하도록 하고,
이 생성된 파일이 Github에 commit& push 되도록 셋팅 하고자 한다.
작업순서
1. 블로그의 내용을 스크래핑 하는 파이썬 파일 만들기.
2.스크래핑 한 파일을 로컬 저장소에 자동 저장하도록 환경 설정하기
3.폴더에 파일 변화를 감지하는 파이썬 파일 만들기 ( 변경시 Git commit & Push)
4.동작 확인하기
간략화 한 흐름도
1. 블로그의 내용을 스크래핑 하는 파이썬 파일 만들기
- 먼저 git 저장소를 만들어주고 초기화, 원격 저장소와 로컬 저장소를 연결해주었다. (실험용)
실제로는 AWS 폴더와 연결해야 하지만 실험을 위해 로컬 저장소로 실시했다.
-블로그의 내용을 스크래핑 하는 파이썬 파일을 만들어준다. 블로그의 내용은 <div class="tt_article ~~~ > 로 시작하기 때문에 이 클래스 이하를 모두 가져오도록 한다.
- 블로그의 포스팅은
내 블로그 주소/숫자
의 형태로 되었고, 하나의 포스팅이 증가할 때 마다 숫자가 증가하는 방식이다. 따라서 숫자를 1부터 시작해서 다음날에는 2로 증가시키는 방법으로 하루에 1 포스팅을 푸쉬하도록 한다.
파이썬 스크립트를 새로 실행할 때마다 변수는 초기화 되기 때문에, 텍스트 폴더에 변수를 증가해서 저장시키고 다음에 로직이 실행될 때 이 변수를 불러와 명령어들을 실행하고, 변수를 증가하여 저장시킨 후 종료하도록 설계한다.
- 스크래핑을 위해 특정 라이브러리가 필요한데, 파이썬 가상 환경에서 동작시킨다.
import requests
from bs4 import BeautifulSoup
- 완성 된 코드내용
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
- 이 코드를 실행하려면, 가상 환경을 활성화 하고 실행해야 한다. ( 라이브러리의 경우도 가상환경을 통해 설치해야 한다 )
가상 환경을 설정하려면
- venv라는 이름의 가상환경을 만든다.
python3 -m venv venv
- 가상 환경을 활성화 한다. ( 쉘 프롬프트 좌측에 (.venv) 가 생성된다 -> 가상화 활성상태 )
source venv/bin/activate
- 라이브러리를 설치해 준다 ( 이 라이브러리를 설치하면 not import 오류가 없어진다)
pip install requests beautifulsoup4
- 테스트가 끝나고 가상화 종료 방법
deactivate
2.스크래핑 한 파일을 로컬 저장소에 자동 저장하도록 환경 설정하기
-라이브러리가 import 오류가 없고, 스크립트가 제대로 동작하는지 확인하기 위해서 테스트를 진행한다.
현재 시스템 시간으로 14시 08분 이기 때문에 2분 뒤인 14시 10분에 이 스크래핑 파일을 실행하는 스크립트 명령어를 실행한다.
-crontab 편집기를 연다
crontab -e
- 편집기가 열리면 매일 14시 10분에 특정파일이 실행되도록 (가상 환경 포함) 문법에 맞게 입력 후 저장하고 나온다.
10 14 * * * /home/kang/문서/bolg_scrap/.venv/bin/python /home/kang/문서/bolg_scrap/folder/scrape_bog.py
2분을 기다린다....
제발 한 번에 성공하자!!!
원하는 폴더에 제대로 파일이 만들어 진 것을 확인했다!!!
3.폴더에 파일 변화를 감지하는 파이썬 파일 만들기 ( 변경시 Git commit & push)
- watchdog 이라는 라이브러리를 통해서, 내가 설정한 폴더에 변경사항이 생길 경우 자동으로 커밋하는 파이썬 파일을 작성한다.
이 경우, 새로운 파일을 만들거나 변경사항이 생기면 -> 커밋 메시지가 생성 -> 새로운 커밋 메시지를 변경사항으로 받아들이고 -> 또 새로운 커밋을 생성 하는 방식인지, 가만히 놔두니 800개의 커밋이 발생해버렸다.
따라서 한 번 변경사항을 감지하고 10분의 시간차를 두고 변경사항을 감지하도록 설정해놓고, 프로그램은 5분만에 종료하도록 셋팅해서 지정한 시간의 5분내의 변경사항만 커밋 & 푸쉬 하도록 한다.
이 5분 사이에 내 스크래핑 스크립트가 동작해서 md파일을 추가하면 된다.
-작성한 파이썬 파일
import os
import time
import git
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.is_committing = False  # 커밋 중인지 여부를 나타내는 플래그

    def on_created(self, event):
        if event.is_directory or self.is_committing:
            return

        # 무시할 파일 목록
        ignored_files = [
            'COMMIT_EDITMSG',
            'main.lock',
            'HEAD.lock',
            'index.lock'
        ]

        # Git 관련 임시 파일 무시
        if any(event.src_path.endswith(ext) for ext in ['.lock', '.tmp']):
            return

        # 무시 목록에 포함되어 있는지 확인
        if os.path.basename(event.src_path) in ignored_files:
            return

        repo_path = '/home/kang/문서/bolg_scrap'  # Git 저정소가 연결된 로컬 저장소
        repo = git.Repo(repo_path)

        # 커밋 중 플래그 설정
        self.is_committing = True

        try:
            # 변경 사항 추가 및 커밋
            repo.git.add(A=True)
            commit_message = f"Added: {os.path.basename(event.src_path)}"
            repo.index.commit(commit_message)
            print(f"Committed: {commit_message}")

            # 푸시 (upstream 설정 포함)
            repo.git.push('origin', 'main')  # 원격 브랜치 설정 포함
            print(f"Pushed: {commit_message}")

        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            # 커밋이 끝난 후 대기
            time.sleep(600)  # 10분 대기
            self.is_committing = False

if __name__ == "__main__":
    path = '/home/kang/문서/bolg_scrap'  # 감지할 폴더
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)

    observer.start()
    print(f"Watching for changes in {path}...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
4. 동작 확인하기
-시나리오
파일 변경 감지 스크립트가 지정한 시간에 실행된다
시간차 ( 약 1분 이내 )를 두고 블로그 스크래핑 스크립트가 실행된다
블로그 글을 스크래핑 하여 md 파일로 저장하고 스크래핑 스크립트를 종료한다.
변경 감지가 확인되면 커밋하고 푸쉬한다.
파일 변경 감지 스크립트를 종료시킨다
현재 시간 17시 00분 이기 때문에
- 17시 02분에 파일 변경 감지 확인 스크립트 실행 (월,화,수.목,금 17시 02분에 시작)
- 17시 03분에 블로그 포스팅 스크래핑 실행 -> md 파일 생성 및 저장
- 변경감지가 17시 03분에 종료되므로 이 안에 새로운 변경이 감지되면 commit & push 가 될 것이다.
기다려보자
17시 02분에 변경감지 스크립트가 실행되어 PID 가 부여 되었다.
17시 03분에 새로운 파일이 생성되었다.
새로운 커밋이 Push 되었다!!
마무리
생각보다 긴 시간동안 설정 사항들을 수정해 가면서 해당 사항들을 구현해 봤다.
서버용 컴퓨터가 아니기 때문에, 일단 특정 시간에만 동작하도록 구현 해 봤고, 이 설정들을 가지고 AWS EC2 에 올려놓고 동작시킨다면 자동화가 될 것이다. (근데 비용이 무서워서 실험만 해보고 안 쓸듯)
또 컴퓨터 부팅 후에 해당 스크립트들을 동작시킬 수 있는데, 이 역시 매일 컴퓨터를 켜 줘야 하기 때문에 이 방법도 나쁘지 않을 것 같다.
무한 루프 때문에 생겨버린 자동 커밋 840개... 이건 어쩌냐ㅜㅜ