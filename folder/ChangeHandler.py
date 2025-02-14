import os
import time
import git
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        repo_path = '/home/kang/문서/bolg_scrap'  # Git 저장소 경로
        repo = git.Repo(repo_path)

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
