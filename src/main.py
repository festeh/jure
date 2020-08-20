from argparse import ArgumentParser
from pathlib import Path
from time import sleep
from watchdog.observers import Observer

from src.handlers import SeleniumHandler, WatchdogHandler
from src.utils import get_file_path_from_notebook_path


def main(file_path, notebook_path, token):
    assert Path(file_path).exists(), print(file_path)
    page = f"http://localhost:8888/notebooks/{notebook_path}?token={token}"
    handler = SeleniumHandler(page)
    observer = Observer()
    event_handler = WatchdogHandler(file_path, handler)
    observer.schedule(event_handler, file_path)
    observer.start()
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        handler.shutdown()
    observer.join()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--jupyter_root_dir", type=Path, required=True)
    parser.add_argument("--notebook_path", type=Path, required=True)
    parser.add_argument("--token", required=True)
    args = parser.parse_args()
    notebook_path = args.notebook_path
    file_path = get_file_path_from_notebook_path(notebook_path)
    notebook_relative_path = notebook_path.relative_to(args.jupyter_root_dir)
    main(file_path, notebook_relative_path, args.token)
