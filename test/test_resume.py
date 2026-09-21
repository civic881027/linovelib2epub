import json
import logging
import pickle

import pytest

from linovelib2epub.models import CatalogLinovelibChapter, CatalogLinovelibVolume, LightNovel
from linovelib2epub.resume import INDEX_VERSION, ResumeStore, apply_index, index_payload
from linovelib2epub.spider.linovelib_spider import LinovelibSpiderPC


def a_catalog():
    return [
        CatalogLinovelibVolume(vid=1, volume_title='v1', chapters=[
            CatalogLinovelibChapter(chapter_title='c1', chapter_url='http://x/1.html'),
            CatalogLinovelibChapter(chapter_title='c2', chapter_url='javascript:cid(0)'),
        ]),
        CatalogLinovelibVolume(vid=2, volume_title='v2', chapters=[
            CatalogLinovelibChapter(chapter_title='c3', chapter_url='http://x/3.html'),
        ]),
    ]


def a_spider(tmp_path, monkeypatch, **settings):
    monkeypatch.chdir(tmp_path)
    spider = LinovelibSpiderPC.__new__(LinovelibSpiderPC)
    spider.spider_settings = {'book_id': 1, 'http_retries': 0, 'select_volume_mode': False,
                              'pickle_temp_folder': 'pickle', 'log_filename': 'book', 'resume': True}
    spider.spider_settings.update(settings)
    spider.logger = logging.getLogger('test')
    # the spider is built without __init__, so supply what the content loop reads
    spider._html_content_id = 'TextContent'
    spider._mapping_dict = {}
    return spider


# ---------- the chapter-link index ----------

def test_index_round_trip_restores_resolved_links(tmp_path):
    catalog = a_catalog()
    catalog[0].chapters[1].chapter_url = 'http://x/2.html'  # a broken link, resolved while crawling
    catalog[0].chapters[1].add_expand_paginated_chapter_url('http://x/2_2.html')
    store = ResumeStore(str(tmp_path), 'book')
    store.save_index(catalog, {1: 'http://x/3.html', 2: 'http://x/4.html'})

    fresh = a_catalog()
    restored = apply_index(fresh, store.load_index())

    assert restored == {1: 'http://x/3.html', 2: 'http://x/4.html'}
    assert fresh[0].chapters[1].chapter_url == 'http://x/2.html'
    assert fresh[0].chapters[1].other_paginated_chapter_urls == ['http://x/2_2.html']


def test_a_half_built_index_only_restores_the_volumes_it_finished(tmp_path):
    catalog = a_catalog()
    catalog[0].chapters[1].chapter_url = 'http://x/2.html'
    store = ResumeStore(str(tmp_path), 'book')
    store.save_index(catalog, {1: 'http://x/3.html'})  # interrupted before volume 2

    fresh = a_catalog()
    restored = apply_index(fresh, store.load_index())

    assert restored == {1: 'http://x/3.html'}
    assert fresh[0].chapters[1].chapter_url == 'http://x/2.html'
    assert fresh[1].chapters[0].chapter_url == 'http://x/3.html'  # untouched, still to be walked


def test_index_is_rejected_when_the_book_gained_a_chapter():
    saved = index_payload(a_catalog(), {1: '', 2: ''})
    grown = a_catalog()
    grown[1].chapters.append(CatalogLinovelibChapter(chapter_title='c4', chapter_url='http://x/4.html'))

    assert apply_index(grown, saved) == {}


def test_a_rejected_index_leaves_the_catalog_untouched():
    saved = index_payload(a_catalog(), {1: '', 2: ''})
    saved['volumes'][0]['vid'] = 99  # no longer describes this catalog
    catalog = a_catalog()

    assert apply_index(catalog, saved) == {}
    assert catalog[0].chapters[1].chapter_url == 'javascript:cid(0)'


@pytest.mark.parametrize('payload', [None, {}, {'version': INDEX_VERSION + 1, 'volumes': []}])
def test_index_is_rejected_when_absent_or_from_another_version(payload):
    assert apply_index(a_catalog(), payload) == {}


def test_a_finished_volume_without_a_usable_link_is_rejected():
    saved = index_payload(a_catalog(), {1: '', 2: ''})
    saved['volumes'][0]['chapters'][0]['url'] = ''

    assert apply_index(a_catalog(), saved) == {}


def test_load_index_returns_none_for_a_damaged_file(tmp_path):
    store = ResumeStore(str(tmp_path), 'book')
    store.save_index(a_catalog(), {})
    with open(store.index_path, 'w', encoding='utf-8') as file:
        file.write('{ this is not json')

    assert store.load_index() is None


def test_saved_index_is_readable_json(tmp_path):
    store = ResumeStore(str(tmp_path), 'book')
    store.save_index(a_catalog(), {1: 'http://x/3.html'})

    with open(store.index_path, encoding='utf-8') as file:
        payload = json.load(file)
    assert payload['version'] == INDEX_VERSION
    assert [volume['vid'] for volume in payload['volumes']] == [1, 2]
    assert [volume['indexed'] for volume in payload['volumes']] == [True, False]


# ---------- the per-volume checkpoint ----------

def test_partial_round_trip(tmp_path):
    store = ResumeStore(str(tmp_path), 'book')
    novel = LightNovel(book_title='書名')
    novel.add_volume(vid=1, title='v1')

    store.save_partial(novel)

    restored = store.load_partial()
    assert restored.book_title == '書名'
    assert [volume.volume_id for volume in restored.volumes] == [1]


def test_load_partial_returns_none_for_a_damaged_file(tmp_path):
    store = ResumeStore(str(tmp_path), 'book')
    store.save_partial(LightNovel())
    with open(store.partial_path, 'wb') as file:
        file.write(b'not a pickle')

    assert store.load_partial() is None


def test_clear_removes_both_files_and_tolerates_their_absence(tmp_path):
    store = ResumeStore(str(tmp_path), 'book')
    store.save_index(a_catalog(), {1: 'a', 2: 'b'})
    store.save_partial(LightNovel())

    store.clear()
    store.clear()  # a second run must not raise

    assert store.load_index() is None and store.load_partial() is None


# ---------- the spider side ----------

def test_finished_volumes_come_back_and_are_reported(tmp_path, monkeypatch):
    spider = a_spider(tmp_path, monkeypatch)
    store = spider._resume_store()
    saved = LightNovel()
    saved.add_volume(vid=1, title='v1')
    store.save_partial(saved)

    novel, finished = spider._load_finished_volumes(a_catalog(), store, {1: 'http://x/3.html'})

    assert finished == {1}
    assert [volume.volume_id for volume in novel.volumes] == [1]


def test_a_volume_the_user_no_longer_wants_is_dropped(tmp_path, monkeypatch):
    spider = a_spider(tmp_path, monkeypatch)
    store = spider._resume_store()
    saved = LightNovel()
    saved.add_volume(vid=1, title='v1')
    saved.add_volume(vid=7, title='a volume that is not in this run')
    store.save_partial(saved)

    novel, finished = spider._load_finished_volumes(a_catalog(), store, {1: 'a', 7: 'b'})

    assert finished == {1}
    assert [volume.volume_id for volume in novel.volumes] == [1]


def test_a_volume_is_not_skipped_without_its_boundary_link(tmp_path, monkeypatch):
    # skipping it would leave the next volume unable to resolve a broken chapter link
    spider = a_spider(tmp_path, monkeypatch)
    store = spider._resume_store()
    saved = LightNovel()
    saved.add_volume(vid=1, title='v1')
    store.save_partial(saved)

    novel, finished = spider._load_finished_volumes(a_catalog(), store, {})

    assert finished == set()
    assert novel.volumes == []


def test_nothing_is_reused_when_resume_is_off(tmp_path, monkeypatch):
    spider = a_spider(tmp_path, monkeypatch, resume=False)
    store = spider._resume_store()
    saved = LightNovel()
    saved.add_volume(vid=1, title='v1')
    store.save_partial(saved)

    novel, finished = spider._load_finished_volumes(a_catalog(), store, {1: 'a'})

    assert finished == set()
    assert novel.volumes == []


def a_two_volume_crawl(tmp_path, monkeypatch, **settings):
    """A spider whose catalog has two chapterless volumes, so nothing is fetched over the wire."""
    spider = a_spider(tmp_path, monkeypatch, **settings)
    catalog = [CatalogLinovelibVolume(vid=1, volume_title='v1'),
               CatalogLinovelibVolume(vid=2, volume_title='v2')]
    monkeypatch.setattr(spider, '_fetch_catalog', lambda *args, **kwargs: '<html/>')
    monkeypatch.setattr(spider, '_convert_to_catalog_list', lambda html: catalog)
    monkeypatch.setattr(spider, '_remove_duplicate_images_in_html', lambda chapter_list: None)
    return spider, catalog


def test_a_finished_volume_is_not_fetched_again(tmp_path, monkeypatch):
    spider, catalog = a_two_volume_crawl(tmp_path, monkeypatch)
    store = spider._resume_store()
    saved = LightNovel()
    saved.add_volume(vid=1, title='v1')
    store.save_partial(saved)
    store.save_index(catalog, {1: 'http://x/boundary.html'})

    novel = spider._crawl_book_content('http://example.invalid/catalog')

    assert [volume.volume_id for volume in novel.volumes] == [1, 2]
    assert novel.volumes[0].title == 'v1'  # restored, not crawled again


def test_skipping_a_volume_hands_its_boundary_link_to_the_next_one(tmp_path, monkeypatch):
    spider, catalog = a_two_volume_crawl(tmp_path, monkeypatch)
    catalog[1].chapters.append(CatalogLinovelibChapter(chapter_title='c1', chapter_url='javascript:cid(0)'))
    store = spider._resume_store()
    saved = LightNovel()
    saved.add_volume(vid=1, title='v1')
    store.save_partial(saved)
    store.save_index(catalog, {1: 'http://x/boundary.html'})

    seen = []
    monkeypatch.setattr(spider, '_expand_paginated_chapter_links',
                        lambda chapter, url_next: seen.append(url_next) or 'after')
    monkeypatch.setattr(spider, '_apply_crawl_delay', lambda name: None)
    # the content loop only stops once the page parses; an empty one would retry for ever
    page = '<div id="mlfy_main_text"><h1>c1</h1><div id="TextContent"><p>hi</p></div></div>'
    monkeypatch.setattr(spider, '_fetch_page', lambda *args, **kwargs: page)

    spider._crawl_book_content('http://example.invalid/catalog')

    # volume 2 starts from where volume 1 stopped, not from an empty string
    assert seen == ['http://x/boundary.html']


def test_each_finished_volume_records_its_content_and_its_links(tmp_path, monkeypatch):
    spider, catalog = a_two_volume_crawl(tmp_path, monkeypatch)
    store = spider._resume_store()
    monkeypatch.setattr(spider, '_resume_store', lambda: store)
    saved_volumes, saved_indexes = [], []
    original_partial, original_index = store.save_partial, store.save_index
    store.save_partial = lambda novel: saved_volumes.append(len(novel.volumes)) or original_partial(novel)
    store.save_index = lambda catalog_list, indexed: saved_indexes.append(sorted(indexed)) or original_index(catalog_list, indexed)

    spider._crawl_book_content('http://example.invalid/catalog')

    assert saved_volumes == [1, 2]
    assert saved_indexes == [[1], [1, 2]]
    with open(store.partial_path, 'rb') as file:
        assert len(pickle.load(file).volumes) == 2


def test_the_browser_is_released_when_the_spider_is_closed(tmp_path, monkeypatch):
    from unittest.mock import Mock

    spider = a_spider(tmp_path, monkeypatch)
    driver = Mock()
    spider._driver = driver
    spider._is_driver_initialized = True

    spider.close()

    driver.quit.assert_called_once_with()
    assert spider._driver is None and spider._is_driver_initialized is False


def test_closing_twice_is_harmless(tmp_path, monkeypatch):
    from unittest.mock import Mock

    spider = a_spider(tmp_path, monkeypatch)
    spider._driver = Mock(quit=Mock(side_effect=OSError('already gone')))

    spider.close()
    spider.close()

    assert spider._driver is None
