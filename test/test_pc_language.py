import logging
from types import SimpleNamespace
from unittest.mock import Mock

from linovelib2epub.models import LightNovel
from linovelib2epub.spider.linovelib_spider import LinovelibSpiderPC

BOOK_HTML = '''<html><body>
<h1 class="book-name">歎息的亡靈想引退</h1>
<div class="au-name"> 槻影 </div>
<div class="book-dec"><p>簡介</p></div>
<div class="book-img"><img src="https://img.example/cover.jpg?x=1"></div>
</body></html>'''


def _spider():
    spider = LinovelibSpiderPC.__new__(LinovelibSpiderPC)
    spider.spider_settings = {'book_id': 2978, 'traditional': True, 'base_url': 'https://www.linovelib.com',
                              'pickle_temp_folder': 'pickle'}
    spider.logger = logging.getLogger('test')
    return spider


class FakeButton:
    def __init__(self, page):
        self.page = page

    @property
    def text(self):
        return self.page.label

    def click(self):
        self.page.clicks += 1


class FakePage:
    """Mimics GB_BIG5.js: some polls after the click, the DOM is converted and the label flips."""

    def __init__(self, label, flip_after_polls):
        self.label = label
        self.flip_after_polls = flip_after_polls
        self.clicks = 0
        self.polls_since_click = 0
        self.html = '<h1 class="book-name">叹息</h1>'

    def get(self, url):
        pass

    def ele(self, selector):
        assert selector == '#GB_BIG'
        if self.clicks:
            self.polls_since_click += 1
            if self.polls_since_click > self.flip_after_polls:
                self.label = '简体化'
                self.html = '<h1 class="book-name">歎息</h1>'
        return FakeButton(self)


def test_parse_book_basic_info_reads_given_html():
    assert _spider()._parse_book_basic_info(BOOK_HTML) == (
        '歎息的亡靈想引退', '槻影', '簡介', 'https://img.example/cover.jpg')


def test_convert_page_language_waits_until_page_is_converted():
    spider = _spider()
    page = FakePage('繁體化', flip_after_polls=3)
    spider._driver = page

    spider._convert_page_language('https://www.linovelib.com/novel/2978.html')

    assert page.clicks == 1
    assert '歎息' in page.html


def test_convert_page_language_skips_click_when_already_traditional():
    spider = _spider()
    page = FakePage('简体化', flip_after_polls=0)
    spider._driver = page

    spider._convert_page_language('https://www.linovelib.com/novel/2978.html')

    assert page.clicks == 0


def test_fetch_takes_basic_info_from_converted_browser_page(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # fetch() creates the pickle folder in CWD
    spider = _spider()
    spider._is_driver_initialized = True
    spider._driver = SimpleNamespace(html=BOOK_HTML)
    spider._convert_page_language = Mock()
    spider._crawl_book_content = Mock(return_value=LightNovel())

    novel = spider.fetch()

    assert novel.book_title == '歎息的亡靈想引退'
    assert novel.author == '槻影'
    assert novel.book_cover.remote_src == 'https://img.example/cover.jpg'
