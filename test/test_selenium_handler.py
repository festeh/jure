from os import kill
from pathlib import Path
from signal import SIGKILL
from time import sleep

import pytest
from selenium.webdriver.common.keys import Keys
from watchdog.observers import Observer

from jure.events import reload_event
from jure.handlers import SeleniumHandler, WatchdogHandler, AngryHandler
from test.utils import start_jupyter_server, modify_ipynb_file

this_dir = Path(__file__).parent
TEST_NOTEBOOK_PATH = this_dir / "data/test_notebook.ipynb"
TEST_FILE_PATH = this_dir / "data/test_file.txt"
NOTEBOOK_PAGE = "http://localhost:8814/notebooks/data/test_notebook.ipynb?token=token"


def test_works_alert():
    jupid = start_jupyter_server()
    handler = SeleniumHandler(NOTEBOOK_PAGE)
    driver = handler.driver
    sleep(1.0)
    try:
        cell = driver.find_element_by_class_name("CodeMirror")
        cell.click()
        cell.find_element_by_tag_name("textarea").send_keys(" hello")
        modify_ipynb_file("data/test_notebook.ipynb")
        driver.find_element_by_tag_name("body").send_keys(Keys.CONTROL + "s")
        sleep(0.5)
        handler.handle(reload_event)
    finally:
        kill(jupid, SIGKILL)


def test_does_not_reload_notebook_save():
    """
    Tests that if a change is made to notebook in browser, reload does not happen.
    """
    jupid = start_jupyter_server()
    file_path = TEST_NOTEBOOK_PATH
    watchdog_handler = WatchdogHandler(file_path,
                                       AngryHandler())
    selenium_handler = SeleniumHandler(NOTEBOOK_PAGE)
    driver = selenium_handler.driver
    sleep(0.5)
    try:
        observer = Observer()
        observer.schedule(watchdog_handler, file_path)
        observer.start()
        sleep(0.5)
        cell = driver.find_element_by_class_name("CodeMirror")
        cell.click()
        cell.find_element_by_tag_name("textarea").send_keys(" hello")
        driver.find_element_by_tag_name("body").send_keys(Keys.CONTROL + "s")
        sleep(1.5)
        observer.stop()
        observer.join()
    finally:
        kill(jupid, SIGKILL)


if __name__ == '__main__':
    pytest.main()