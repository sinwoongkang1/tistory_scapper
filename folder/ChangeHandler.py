import os
import time
import git
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
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

        repo_path = '/home/kang/문서/bolg_scrap'  # 올바른 Git 저장소 경로
        repo = git.Repo(repo_path)

        # 변경 사항 추가 및 커밋
        repo.git.add(A=True)
        commit_message = f"Added: {os.path.basename(event.src_path)}"
        repo.index.commit(commit_message)
        print(f"Committed: {commit_message}")



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
