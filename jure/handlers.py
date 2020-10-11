from sys import stderr
from time import sleep
from typing import List

from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from watchdog.events import FileSystemEventHandler

from jure.events import reload_event, cells_changed_event, EventType
from jure.index_notebook_cells import CellsIndex
from jure.utils import get_notebook_path_from_file_path, get_lines_file, get_file_update_timestamp, get_diffing_lines

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
        try:
            self.driver.get(page)
        except WebDriverException as e:
            msg = f"""Unable to load Jupyter Notebook.
                      Make sure that Jupyter Notebook is available on page {page}"""
            raise RuntimeError(msg)

    def handle(self, event):
        if event['type'] == EventType.RELOAD_PAGE:
            self._refresh_page()
        if event['type'] == EventType.HANDLE_CHANGED_CELLS:
            self._scroll_to_cell(event['cell_to_scroll'])
            self._execute_cells(event['changed_cells'])

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

    def _execute_cells(self, changed_cells: List[str]):
        logger.info(f"Executing cells {changed_cells}")
        if changed_cells:
            exec_script = f"""
                Jupyter.notebook.execute_cells([{','.join(changed_cells)}]);
                """
            logger.info(exec_script)
            self.driver.execute_script(exec_script)

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
            try:
                self.handler.handle(reload_event)
                new_lines = get_lines_file(self.file_path)
                diffing_lines = get_diffing_lines(self.file_lines, new_lines)
                self.file_lines = new_lines
                cells_index = CellsIndex(new_lines)
                if not diffing_lines:
                    cell_to_scroll = cells_index.get_last_cell()
                else:
                    cell_to_scroll = cells_index.get_cell(diffing_lines[-1])
                diffing_cells = set()
                for line in diffing_lines:
                    diffing_cells.add(cells_index.get_cell(line))
                diffing_cells = [str(cell) for cell in sorted(diffing_cells)]
                new_scroll_event = cells_changed_event(cell_to_scroll=cell_to_scroll,
                                                       diffing_cells=diffing_cells)
                logger.info(str(new_scroll_event))
                self.handler.handle(new_scroll_event)
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
