"""Each finished volume becomes an epub straight away, instead of all of them at the end."""
import logging
from types import SimpleNamespace
from unittest.mock import Mock

from linovelib2epub.linovel import EpubWriter, Linovelib2Epub
from linovelib2epub.models import LightNovel, LightNovelVolume
from linovelib2epub.spider.linovelib_spider import LinovelibSpiderPC


def a_spider(handler=None, basic_info=('書名', '作者', '簡介', 'cover-image')):
    spider = LinovelibSpiderPC.__new__(LinovelibSpiderPC)
    spider.spider_settings = {'book_id': 2971, 'on_volume_ready': handler}
    spider.logger = logging.getLogger('test')
    spider._novel_basic_info = basic_info
    return spider


def a_volume(volume_id=1, title='v1'):
    return LightNovelVolume(volume_id=volume_id, title=title)


def a_writer(divide_volume=True, tmp_path=None, monkeypatch=None):
    if monkeypatch is not None:
        monkeypatch.chdir(tmp_path)  # the logger writes to ./logs
    return EpubWriter({'divide_volume': divide_volume, 'has_illustration': False,
                       'image_download_folder': 'novel_images', 'log_filename': 'test'})


# ---------- handing a finished volume over ----------

def test_a_finished_volume_is_handed_over_with_the_book_details():
    handed = []
    spider = a_spider(handler=handed.append)

    spider._emit_volume(a_volume())

    assert len(handed) == 1
    novel = handed[0]
    assert novel.book_title == '書名' and novel.author == '作者'
    assert novel.book_cover == 'cover-image'
    assert [volume.volume_id for volume in novel.volumes] == [1]
    assert novel.basic_info_ready and novel.volumes_content_ready


def test_nothing_is_handed_over_without_a_handler():
    a_spider(handler=None)._emit_volume(a_volume())  # must not raise


def test_nothing_is_handed_over_before_the_book_page_was_read():
    handed = []
    spider = a_spider(handler=handed.append, basic_info=None)

    spider._emit_volume(a_volume())

    assert handed == []


def test_a_failure_while_writing_one_volume_does_not_end_the_crawl():
    def explode(novel):
        raise OSError('disk full')

    a_spider(handler=explode)._emit_volume(a_volume())  # swallowed; the final write retries it


# ---------- not writing the same epub twice ----------

def test_the_final_write_skips_volumes_already_written(tmp_path, monkeypatch):
    writer = a_writer(tmp_path=tmp_path, monkeypatch=monkeypatch)
    writer._write_epub = Mock()
    novel = LightNovel(book_title='書名', author='作者',
                       book_cover=SimpleNamespace(local_relative_path='cover.jpg'),
                       volumes=[a_volume(1, 'v1'), a_volume(2, 'v2'), a_volume(3, 'v3')])

    writer.write(novel, already_written={1, 3})

    assert [call.args[0] for call in writer._write_epub.call_args_list] == ['v2']


def test_the_final_write_covers_everything_when_nothing_was_written_yet(tmp_path, monkeypatch):
    writer = a_writer(tmp_path=tmp_path, monkeypatch=monkeypatch)
    writer._write_epub = Mock()
    novel = LightNovel(book_title='書名', author='作者',
                       book_cover=SimpleNamespace(local_relative_path='cover.jpg'),
                       volumes=[a_volume(1, 'v1'), a_volume(2, 'v2')])

    writer.write(novel)

    assert [call.args[0] for call in writer._write_epub.call_args_list] == ['v1', 'v2']


# ---------- the crawler side of the hand-off ----------

def a_crawler(divide_volume=True):
    crawler = Linovelib2Epub.__new__(Linovelib2Epub)
    crawler.common_settings = {'divide_volume': divide_volume}
    crawler._written_volume_ids = set()
    crawler._spider = Mock()
    crawler._epub_writer = Mock()
    return crawler


def test_a_volume_is_downloaded_and_written_as_soon_as_it_is_ready():
    crawler = a_crawler()
    novel = LightNovel(volumes=[a_volume(2, 'v2')])

    crawler._write_finished_volume(novel)

    crawler._spider.download_images.assert_called_once_with(novel)
    crawler._epub_writer.write.assert_called_once_with(novel)
    assert crawler._written_volume_ids == {2}


def test_one_epub_for_the_whole_book_is_still_written_only_at_the_end():
    crawler = a_crawler(divide_volume=False)

    crawler._write_finished_volume(LightNovel(volumes=[a_volume(1, 'v1')]))

    crawler._spider.download_images.assert_not_called()
    crawler._epub_writer.write.assert_not_called()
    assert crawler._written_volume_ids == set()
