"""A stop request ends the crawl at its next pause instead of after the whole book."""
import logging
import threading
import time

import pytest

from linovelib2epub.exceptions import CrawlStopped
from linovelib2epub.spider.linovelib_spider import PAGE_RETRY_PAUSE_SECONDS, LinovelibSpiderPC


def a_spider(stop_event=None, **settings):
    spider = LinovelibSpiderPC.__new__(LinovelibSpiderPC)
    spider.spider_settings = {'book_id': 1, 'stop_event': stop_event, 'chapter_crawl_delay': 5}
    spider.spider_settings.update(settings)
    spider.logger = logging.getLogger('test')
    return spider


def test_a_requested_stop_ends_the_delay_at_once():
    event = threading.Event()
    event.set()
    started = time.monotonic()

    with pytest.raises(CrawlStopped):
        a_spider(event)._apply_crawl_delay('chapter_crawl_delay')

    assert time.monotonic() - started < 1


def test_a_stop_during_the_delay_does_not_wait_it_out():
    event = threading.Event()
    threading.Timer(0.1, event.set).start()
    started = time.monotonic()

    with pytest.raises(CrawlStopped):
        a_spider(event)._apply_crawl_delay('chapter_crawl_delay')

    assert time.monotonic() - started < 2


def test_a_zero_delay_still_notices_the_stop():
    event = threading.Event()
    event.set()

    with pytest.raises(CrawlStopped):
        a_spider(event, chapter_crawl_delay=0)._apply_crawl_delay('chapter_crawl_delay')


def test_the_delay_runs_out_normally_while_no_stop_is_requested():
    # Windows timers are coarse, so do not measure the wait; check it happened and did not raise
    event = threading.Event()
    waited = []
    event.wait = lambda seconds: waited.append(seconds) or False  # timed out, no stop

    a_spider(event, chapter_crawl_delay=3)._apply_crawl_delay('chapter_crawl_delay')

    assert waited == [3]


def test_without_a_stop_signal_the_delay_is_a_plain_sleep(monkeypatch):
    slept = []
    monkeypatch.setattr('linovelib2epub.spider.base_spider.time.sleep', lambda seconds: slept.append(seconds))

    a_spider(None, chapter_crawl_delay=3)._apply_crawl_delay('chapter_crawl_delay')

    assert slept == [3]


def test_the_rate_limit_pause_also_gives_up_when_stopped():
    event = threading.Event()
    event.set()
    started = time.monotonic()

    with pytest.raises(CrawlStopped):
        a_spider(event)._pause_before_page_retry('http://x/1.html', 1)

    assert time.monotonic() - started < min(1, PAGE_RETRY_PAUSE_SECONDS)
