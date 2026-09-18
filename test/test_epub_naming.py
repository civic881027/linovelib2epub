import logging
from types import SimpleNamespace
from unittest.mock import Mock

from linovelib2epub.linovel import EpubWriter
from linovelib2epub.models import CatalogLinovelibVolume, LightNovel, LightNovelVolume
from linovelib2epub.spider.linovelib_spider import LinovelibSpiderPC


def _writer(tmp_path, monkeypatch, divide_volume):
    monkeypatch.chdir(tmp_path)  # Logger writes to ./logs
    return EpubWriter({
        'divide_volume': divide_volume,
        'has_illustration': False,
        'image_download_folder': 'novel_images',
        'log_filename': 'test',
    })


def _novel():
    return LightNovel(
        book_title='書名',
        author='作者',
        book_cover=SimpleNamespace(local_relative_path='cover.jpg'),
        volumes=[LightNovelVolume(volume_id=1, title='書名 1 白狼之巢'),
                 LightNovelVolume(volume_id=3, title='書名 3 拍賣會')],
    )


def test_divide_volume_epub_title_is_volume_title_only(tmp_path, monkeypatch):
    # The output folder is already named after the book, so the file name must not repeat it.
    writer = _writer(tmp_path, monkeypatch, divide_volume=True)
    writer._write_epub = Mock()

    writer.write(_novel())

    titles = [call.args[0] for call in writer._write_epub.call_args_list]
    assert titles == ['書名 1 白狼之巢', '書名 3 拍賣會']


def test_single_epub_title_is_book_title(tmp_path, monkeypatch):
    writer = _writer(tmp_path, monkeypatch, divide_volume=False)
    writer._write_epub = Mock()

    writer.write(_novel())

    assert writer._write_epub.call_args.args[0] == '書名'


def test_selected_volume_keeps_catalog_position(monkeypatch):
    # Selecting only the third volume must still yield volume_id 3 (=> "03." prefix), not 0.
    spider = LinovelibSpiderPC.__new__(LinovelibSpiderPC)
    spider.spider_settings = {'book_id': 1, 'http_retries': 0, 'select_volume_mode': True}
    spider.logger = logging.getLogger('test')
    catalog = [CatalogLinovelibVolume(vid=1, volume_title='v1'),
               CatalogLinovelibVolume(vid=2, volume_title='v2'),
               CatalogLinovelibVolume(vid=3, volume_title='v3')]
    monkeypatch.setattr(spider, '_fetch_catalog', lambda *args, **kwargs: '<html/>')
    monkeypatch.setattr(spider, '_convert_to_catalog_list', lambda html: catalog)
    monkeypatch.setattr(spider, '_handle_select_volume', lambda catalog_list: [catalog_list[2]])
    monkeypatch.setattr(spider, '_remove_duplicate_images_in_html', lambda chapter_list: None)

    novel = spider._crawl_book_content('http://example.invalid/catalog')

    assert [volume.volume_id for volume in novel.volumes] == [3]
