"""The log file of a book holds only its latest run."""
import logging
from unittest.mock import Mock

from linovelib2epub import Linovelib2Epub, TargetSite
from linovelib2epub import linovel as linovel_module
from linovelib2epub import logger as logger_module
from linovelib2epub.logger import Logger, start_fresh_log


def test_starting_fresh_empties_the_previous_run(tmp_path):
    path = tmp_path / 'logs' / 'www.linovelib.com_2974.log'
    path.parent.mkdir()
    path.write_text('old run\n', encoding='utf-8')

    assert start_fresh_log('www.linovelib.com_2974', str(tmp_path / 'logs')) == str(path)

    assert path.read_text(encoding='utf-8') == ''


def test_starting_fresh_creates_the_folder_and_file(tmp_path):
    path = start_fresh_log('book', str(tmp_path / 'logs'))

    assert (tmp_path / 'logs' / 'book.log').exists() and open(path).read() == ''


def test_lines_of_the_new_run_still_arrive_after_the_reset(tmp_path, monkeypatch):
    monkeypatch.setattr(logger_module, 'DEFAULT_LOG_FOLDER', str(tmp_path / 'logs'))
    Logger(logger_name='before', log_filename='book').get_logger().info('from the previous run')
    logging.getLogger('before').handlers.clear()

    start_fresh_log('book')
    Logger(logger_name='after', log_filename='book').get_logger().info('from this run')
    logging.getLogger('after').handlers.clear()

    text = (tmp_path / 'logs' / 'book.log').read_text(encoding='utf-8')
    assert 'from this run' in text and 'from the previous run' not in text


def test_the_crawler_resets_the_log_before_its_spider_writes_to_it(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(logger_module, 'DEFAULT_LOG_FOLDER', str(tmp_path / 'logs'))
    order = []
    monkeypatch.setattr(linovel_module, 'start_fresh_log', lambda name: order.append(('reset', name)))
    monkeypatch.setattr(linovel_module, 'LinovelibSpiderPC',
                        lambda spider_settings: order.append(('spider', None)) or Mock())

    Linovelib2Epub(book_id=2974, target_site=TargetSite.LINOVELIB_PC, chapter_crawl_delay=0, page_crawl_delay=0)

    assert order == [('reset', 'www.linovelib.com_2974'), ('spider', None)]
