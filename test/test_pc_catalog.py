"""The PC catalog page comes in three shapes; the parser must find the volumes in all of them.

Books 2976 and 2977 used to parse to nothing: 2976 lists a chapter before its first volume, and
the stray `</ul></div>` after it closes #volume-list early; 2977 has no volume divisions at all.
"""
import logging

import pytest

from linovelib2epub.exceptions import LinovelibException
from linovelib2epub.spider.linovelib_spider import LinovelibSpiderPC

BASE = 'https://www.linovelib.com'


def a_spider(book_title='書名'):
    spider = LinovelibSpiderPC.__new__(LinovelibSpiderPC)
    spider.spider_settings = {'base_url': BASE, 'book_id': 2976, 'http_retries': 0,
                              'select_volume_mode': False, 'resume': False,
                              'pickle_temp_folder': 'pickle', 'log_filename': 'test'}
    spider.logger = logging.getLogger('test')
    spider._novel_basic_info = (book_title, '作者', '簡介', None) if book_title else None
    return spider


def chapter_items(chapters):
    return ''.join(f'<li class="col-4"><a href="/novel/2976/{cid}.html">{name}</a></li>'
                   for cid, name in chapters)


def volume_block(vid, title, chapters):
    """One volume exactly as the site emits it, its own `</ul></div>` included."""
    return (f'<div class="volume clearfix">'
            f'<a href="/novel/2976/vol_{vid}.html" class="volume-cover"><img src="/images/no.svg"/></a>'
            f'<div class="volume-info"><h2 class="v-line">'
            f'<a href="/novel/2976/vol_{vid}.html">{title}</a></h2></div>'
            f'<ul class="chapter-list clearfix">{chapter_items(chapters)}</ul></div>')


def page(inner):
    return f'<html><body><div class="volume-list" id="volume-list">{inner}</div></body></html>'


def summary(catalog):
    return [(volume.vid, volume.volume_title, [chapter.chapter_title for chapter in volume.chapters])
            for volume in catalog]


def test_volumes_nested_in_the_list_are_found():
    html = page(volume_block(11, '第一卷', [(1, 'c1'), (2, 'c2')]) + volume_block(12, '第二卷', [(3, 'c3')]))

    catalog = a_spider()._convert_to_catalog_list(html)

    assert summary(catalog) == [(1, '第一卷', ['c1', 'c2']), (2, '第二卷', ['c3'])]
    assert catalog[0].chapters[0].chapter_url == f'{BASE}/novel/2976/1.html'
    assert catalog[0].volume_cover == '/images/no.svg'


def test_a_chapter_before_the_first_volume_does_not_hide_the_volumes():
    # book 2976: 书籍信息 sits before the first volume, and its closing tags end #volume-list early
    html = page(chapter_items([(147529, '书籍信息')]) + '</ul></div>'
                + volume_block(11, '红色的·告白', [(1, 'c1'), (2, 'c2')])
                + '<div class="index-gox"></div>'
                + volume_block(12, '黄色的·谎言', [(3, 'c3')]))

    catalog = a_spider()._convert_to_catalog_list(html)

    assert summary(catalog) == [(1, '红色的·告白', ['c1', 'c2']), (2, '黄色的·谎言', ['c3'])]


def test_a_book_without_volumes_becomes_one_volume_named_after_the_book():
    # book 2977: the chapters sit straight under #volume-list
    html = page(chapter_items([(1, '插图'), (2, '序章'), (3, '尾声')]))

    catalog = a_spider(book_title='梦魇时刻')._convert_to_catalog_list(html)

    assert summary(catalog) == [(1, '梦魇时刻', ['插图', '序章', '尾声'])]
    assert catalog[0].chapters[1].chapter_url == f'{BASE}/novel/2976/2.html'


def test_the_single_volume_has_an_empty_title_before_the_book_page_was_read():
    catalog = a_spider(book_title=None)._convert_to_catalog_list(page(chapter_items([(1, 'c1')])))

    assert summary(catalog) == [(1, '', ['c1'])]


def test_a_volume_without_chapters_is_dropped():
    html = page(volume_block(11, '第一卷', [(1, 'c1')]) + volume_block(12, '預告', []))

    assert summary(a_spider()._convert_to_catalog_list(html)) == [(1, '第一卷', ['c1'])]


@pytest.mark.parametrize('html', ['<html/>', page('')])
def test_nothing_to_read_gives_an_empty_catalog(html):
    assert a_spider()._convert_to_catalog_list(html) == []


def test_a_catalog_without_any_volume_fails_loudly(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    spider = a_spider()
    monkeypatch.setattr(spider, '_fetch_catalog', lambda *args, **kwargs: page(''))

    with pytest.raises(LinovelibException, match='No volume with chapters'):
        spider._crawl_book_content('http://example.invalid/catalog')
