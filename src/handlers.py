import os
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from watchdog.events import FileSystemEventHandler

from src.index_notebook_cells import CellIndex
from src.events import EventType, reload_event, scroll_event
from src.utils import get_lines_file, get_line_to_scroll
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class BaseHandler:
    def handle(self, event):
        print(event)

    def shutdown(self):
        pass


class SeleniumHandler(BaseHandler):
    def __init__(self, page):
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.set_capability('unhandledPromptBehaviour', 'accept')
        options.add_argument("--disable-popup-blocking")
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("window.onbeforeunload = null;")
        self.driver.get(page)

    def handle(self, event):
        if event["type"] == EventType.RELOAD_PAGE:
            self._refresh_page()
        if event["type"] == EventType.GO_TO_CELL:
            cell_num = event["value"]
            self._scroll_to_cell(cell_num)
            self._execute_cell(cell_num)

    def shutdown(self):
        self.driver.close()

    def _refresh_page(self):
        self.check_popup()
        sleep(0.1)
        self.driver.refresh()

    def _scroll_to_cell(self, cell_num):
        self.check_popup()
        self.driver.execute_script(
            f"""
            var cell = Jupyter.notebook.get_cell({cell_num});
            cell.element[0].scrollIntoView();
            """)

    def _execute_cell(self, cell_num):
        self.driver.execute_script(
            f"""
            Jupyter.notebook.execute_cells([0,{cell_num}]);
            """)

    def check_popup(self):
        try:
            self.driver.switch_to.alert.accept()
        except:
            pass
        reload_btn = None
        try:
            notebook_changed_modal = self.driver.find_element_by_css_selector("body.modal-open")
            reload_btn = notebook_changed_modal.find_element_by_class_name("btn-warning")
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
        self.file_lines = get_lines_file(self.file_path)
        self.old = 0
        self.handler = handler

    def on_modified(self, event):
        print(f'event type: {event}')
        file_updated_timestamp = self.get_file_update_timestamp()
        if (file_updated_timestamp - self.old) > 0.5:
            print("Reloading")
            self.handler.handle(reload_event)
            new_lines = get_lines_file(self.file_path)
            line = get_line_to_scroll(self.file_lines, new_lines)
            self.file_lines = new_lines
            cell_num = CellIndex(new_lines).get_cell(line)
            new_scroll_event = scroll_event(cell_num)
            print(line, new_scroll_event)
            self.handler.handle(new_scroll_event)
        else:
            print("No change")
        self.old = file_updated_timestamp

    def get_file_update_timestamp(self):
        statbuf = os.stat(self.file_path)
        new = statbuf.st_mtime
        print(str(new) + " is new")
        print(str(self.old) + " is old")
        return new


class AngryHandler(BaseHandler):
    def handle(self, event):
        raise RuntimeError("You did a mistake...")
