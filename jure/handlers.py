from sys import stderr
from time import sleep

from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from watchdog.events import FileSystemEventHandler

from jure.events import reload_event, scroll_event, EventType
from jure.index_notebook_cells import CellIndex
from jure.utils import get_notebook_path_from_file_path, get_lines_file, get_file_update_timestamp, get_line_to_scroll

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
        logger.info(f"Scrolling to cell {cell_num}")
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
        self.notebook_path = get_notebook_path_from_file_path(file_path)
        self.file_lines = get_lines_file(self.file_path)
        self.prev_update_timestamp = 0
        self.handler = handler

    def on_modified(self, event):
        logger.info(f'event type: {event}')
        file_update_timestamp = get_file_update_timestamp(self.file_path)
        notebook_update_timestamp = get_file_update_timestamp(self.notebook_path)
        if self.should_reload(file_update_timestamp, notebook_update_timestamp):
            logger.info("Reloading")
            self.handler.handle(reload_event)
            new_lines = get_lines_file(self.file_path)
            line = get_line_to_scroll(self.file_lines, new_lines)
            self.file_lines = new_lines
            cell_num = CellIndex(new_lines).get_cell(line)
            new_scroll_event = scroll_event(cell_num)
            logger.info(f"{line}, {new_scroll_event}")
            self.handler.handle(new_scroll_event)
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
