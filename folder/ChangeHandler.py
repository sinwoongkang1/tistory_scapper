
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
        repo = git.Repo(rep
