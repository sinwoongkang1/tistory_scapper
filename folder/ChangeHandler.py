import os
import git
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.is_committing = False  # 커밋 중인지 여부를 나타내는 플래그

    def on_created(self, event):
        self.handle_event(event)

    def on_modified(self, event):
        self.handle_event(event)

    def handle_event(self, event):
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

        repo_path = '/home/ec2-user/blogScrapper'  # 올바른 Git 저장소 경로
        repo = git.Repo(repo_path)

        # 커밋 중 플래그 설정
        self.is_committing = True

        try:
            # 변경 사항 추가 및 커밋
            repo.git.add(A=True)
            commit_message = f"Updated: {os.path.basename(event.src_path)}"
            repo.index.commit(commit_message)
            print(f"Committed: {commit_message}")

            # 푸시 (upstream 설정 포함)
            repo.git.push('origin', 'main')  # 원격 브랜치 설정 포함
            print(f"Pushed: {commit_message}")

        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            self.is_committing = False  # 커밋이 끝난 후 플래그 해제

if __name__ == "__main__":
    path = '/home/ec2-user/blogScrapper'  # 감지할 폴더
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)

    observer.start()
    print(f"Watching for changes in {path}...")

    try:
        while True:
            pass  # 무한 루프 대신 빈 루프 사용
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
