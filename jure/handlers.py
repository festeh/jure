import json
from sys import stderr
from time import sleep
from typing import List, Dict, Optional

import jupytext
from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from watchdog.events import FileSystemEventHandler

from jure.events import cells_changed_event, EventType
from jure.utils import (
    get_notebook_path_from_file_path,
    get_file_update_timestamp,
    get_file,
)

logger.remove()
logger.add(stderr, format="{time: HH:mm:SSSS} {level} {message}", level="INFO")


class BaseHandler:
    def handle(self, event):
        print(event)

    def shutdown(self):
        pass


class SeleniumHandler(BaseHandler):
    def __init__(self, page):
        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.set_capability("unhandledPromptBehaviour", "accept")
        options.add_argument("--disable-popup-blocking")
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("window.onbeforeunload = null;")
        try:
            self.driver.get(page)
            self.driver.execute_script("Jupyter.notebook.set_autosave_interval(0);")
        except WebDriverException as e:
            msg = f"""Unable to load Jupyter Notebook.
                      Make sure that Jupyter Notebook is available on page {page}"""
            raise RuntimeError(msg)

    def handle(self, event):
        if event["type"] == EventType.RELOAD_PAGE:
            self._refresh_page()
        if event["type"] == EventType.HANDLE_CHANGED_CELLS:
            self._scroll_to_cell(event["cell_to_scroll"])
            self._execute_cells(event["changed_cells"])

    def shutdown(self):
        self.driver.close()

    def _refresh_page(self):
        self.check_popup()
        sleep(0.1)
        self.driver.refresh()
        self.driver.execute_script("Jupyter.notebook.set_autosave_interval(0);")

    def _scroll_to_cell(self, cell_num: Optional[int]):
        self.check_popup()
        if cell_num is not None:
            logger.info(f"Scrolling to cell {cell_num}")
            self.driver.execute_script(
                f"""
                Jupyter.notebook.scroll_to_cell({cell_num});
                """
            )

    def _execute_cells(self, changed_cells: List[Dict]):
        logger.info(f"Executing")
        if changed_cells:
            formatted_cells = [json.dumps(c, ensure_ascii=False) for c in changed_cells]
            update_script = f"""let data = [{','.join(formatted_cells)}];
data.forEach(function (cell) {{
    Jupyter.notebook.get_cell(cell.index).set_text(cell.content)
}});
"""
            try:
                self.driver.execute_script(update_script)
            except:
                self._refresh_page()
            exec_script = f"""
                Jupyter.notebook.execute_cells([{','.join([c["index"] for c in changed_cells])}]);
                """
            self.driver.execute_script(exec_script)

    def check_popup(self):
        try:
            self.driver.switch_to.alert.accept()
        except:
            pass
        reload_btn = None
        try:
            notebook_changed_modal = self.driver.find_element_by_css_selector(
                "body.modal-open"
            )
            reload_btn = notebook_changed_modal.find_element_by_class_name(
                "btn-warning"
            )
        except NoSuchElementException:
            pass
        if reload_btn is not None:
            reload_btn.click()
            try:
                self.driver.switch_to.alert.accept()
            except:
                pass


class WatchdogHandler(FileSystemEventHandler):
    def __init__(self, file_path, handler):
        self.file_path = file_path
        self.notebook_path = get_notebook_path_from_file_path(file_path)
        self.prev_cells = jupytext.reads(get_file(self.file_path), "py:percent")[
            "cells"
        ]
        self.prev_update_timestamp = 0
        self.handler = handler

    def on_modified(self, event):
        logger.info(f"event type: {event}")
        file_update_timestamp = get_file_update_timestamp(self.file_path)
        notebook_update_timestamp = get_file_update_timestamp(self.notebook_path)
        if self.should_reload(file_update_timestamp, notebook_update_timestamp):
            logger.info("Updating notebook text")
            try:
                cells = jupytext.reads(get_file(self.file_path), "py:percent")["cells"]
                diffing_cells = [
                    i
                    for i, cell in enumerate(cells)
                    if i >= len(self.prev_cells)
                    or self.prev_cells[i]["source"] != cell["source"]
                ]
                self.prev_cells = cells
                cell_to_scroll = None
                if diffing_cells:
                    cell_to_scroll = diffing_cells[-1]
                cell_info = [
                    {"index": str(cell_index), "content": cells[cell_index]["source"]}
                    for cell_index in sorted(diffing_cells)
                ]
                new_event = cells_changed_event(
                    cell_to_scroll=cell_to_scroll, diffing_cells=cell_info
                )
                logger.info(f"{new_event['type']}. Changed cells: {diffing_cells}")
                self.handler.handle(new_event)
            except Exception as e:
                logger.exception(e)
        self.prev_update_timestamp = file_update_timestamp

    def should_reload(self, file_update_timestamp, notebook_update_timestamp):
        if (file_update_timestamp - self.prev_update_timestamp) > 0.5:
            if (file_update_timestamp - notebook_update_timestamp) > 0.5:
                return True
            else:
                logger.info("Notebook was recently reloaded: no change")
        else:
            logger.info("File was recently updated: no change")
        return False


class AngryHandler(BaseHandler):
    def handle(self, event):
        raise RuntimeError("You did a mistake...")
