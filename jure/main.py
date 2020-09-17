from argparse import ArgumentParser
from pathlib import Path
from time import sleep
from watchdog.observers import Observer

from jure.handlers import SeleniumHandler, WatchdogHandler
from jure.utils import get_file_path_from_notebook_path


def parse_arguments(args):
    parser = ArgumentParser(description="Reload Selenium browser tab when Jupyter .py file is updated")
    parser.add_argument("--jupyter_root_dir", type=Path, required=True,
                        help="Path to directory where the Jupyter notebook is launched")
    parser.add_argument("--notebook_path", type=Path, required=True,
                        help="Path to notebook file on disk")
    parser.add_argument("--port", default="8888", help="Port on which Jupyter is launched")
    parser.add_argument("--token", required=True, help="Secret token to get access to Jupyter")
    parsed_args = parser.parse_args(args)
    return parsed_args


def main(args=None):
    parsed_args = parse_arguments(args)
    notebook_path = parsed_args.notebook_path
    port = parsed_args.port
    file_path = get_file_path_from_notebook_path(notebook_path)
    assert Path(file_path).exists()
    notebook_relative_path = notebook_path.relative_to(parsed_args.jupyter_root_dir)
    page = f"http://localhost:{port}/notebooks/{notebook_relative_path}?token={parsed_args.token}"
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
    main()
