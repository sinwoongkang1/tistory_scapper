import os
import time
import git
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.is_committing = False  # 커밋 중인지 여부를 나타내는 플래그

    def _handle_event(self, event):
        if event.is_directory or self.is_committing:
            return

        ignored_files = [
            'COMMIT_EDITMSG',
            'main.lock',
            'HEAD.lock',
            'index.lock'
        ]

        if any(event.src_path.endswith(ext) for ext in ['.lock', '.tmp']):
            return

        if os.path.basename(event.src_path) in ignored_files:
            return

        repo_path = '/home/kang/Documents/blog_scrap'
        repo = git.Repo(repo_path)

        self.is_committing = True

        try:
            repo.git.add(A=True)
            commit_message = f"Updated: {os.path.basename(event.src_path)}"
            repo.index.commit(commit_message)
            print(f"Committed: {commit_message}")

            repo.git.push('origin', 'main')
            print(f"Pushed: {commit_message}")

        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            time.sleep(600)  # 10분 대기
            self.is_committing = False

    def on_created(self, event):
        self._handle_event(event)

    def on_modified(self, event):
        self._handle_event(event)

if __name__ == "__main__":
    path = '/home/kang/Documents/blog_scrap'
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





































