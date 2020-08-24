from os import kill
from pathlib import Path
from signal import SIGKILL
from time import sleep

import jupytext
from selenium.webdriver.common.keys import Keys

from src.events import reload_event
from src.handlers import SeleniumHandler
from test.utils import start_jupyter_server

TEST_NOTEBOOK_PATH = Path(__file__).parent / "data/test_notebook.ipynb"
NOTEBOOK_PAGE = "http://localhost:8814/notebooks/data/test_notebook.ipynb?token=token"


def modify_notebook_file(path):
    notebook = jupytext.read(path)
    first_cell = notebook.cells[0]
    first_cell['source'] = first_cell['source'][:-1] + 'a"'
    if len(first_cell['source']) > 10:
        first_cell['source'] = '"a"'
    jupytext.write(notebook, path)


def test_works_alert():
    jupid = start_jupyter_server()
    handler = SeleniumHandler(NOTEBOOK_PAGE)
    driver = handler.driver
    sleep(1.0)
    try:
        cell = driver.find_element_by_class_name("CodeMirror")
        cell.click()
        cell.find_element_by_tag_name("textarea").send_keys(" hello")
        modify_notebook_file("data/test_notebook.ipynb")
        driver.find_element_by_tag_name("body").send_keys(Keys.CONTROL + "s")
        sleep(0.5)
        handler.handle(reload_event)
    finally:
        kill(jupid, SIGKILL)


if __name__ == '__main__':
    test_works_alert()
