import os

import pytest

from linovelib2epub import TargetSite
from linovelib2epub.gui import (DEFAULT_DELAY, DEFAULT_LOG_LEVEL_LABEL, DEFAULT_SITE_LABEL,
                                LOG_LEVEL_CHOICES, SITE_CHOICES, build_kwargs, validate)


def a_form(**overrides):
    form = {
        'book_id': '2978',
        'site_label': DEFAULT_SITE_LABEL,
        'chapter_delay': DEFAULT_DELAY,
        'page_delay': DEFAULT_DELAY,
        'output_dir': os.getcwd(),
        'browser_path': '',
        'log_level_label': DEFAULT_LOG_LEVEL_LABEL,
        'divide_volume': True,
        'select_volume_mode': False,
        'has_illustration': True,
        'headless': True,
    }
    form.update(overrides)
    return form


def test_every_target_site_has_a_chinese_label():
    assert set(SITE_CHOICES.values()) == set(TargetSite)


def test_default_site_is_linovelib_pc_traditional():
    assert SITE_CHOICES[DEFAULT_SITE_LABEL] == TargetSite.LINOVELIB_PC_TRADITIONAL
    # the default must also be the first entry, which is what the dropdown shows first
    assert next(iter(SITE_CHOICES)) == DEFAULT_SITE_LABEL


def test_default_delays_are_five_seconds():
    assert DEFAULT_DELAY == 5


def test_build_kwargs_maps_the_form_to_library_arguments():
    kwargs = build_kwargs(a_form())
    assert kwargs == {
        'book_id': '2978',
        'target_site': TargetSite.LINOVELIB_PC_TRADITIONAL,
        'chapter_crawl_delay': 5,
        'page_crawl_delay': 5,
        'divide_volume': True,
        'select_volume_mode': False,
        'has_illustration': True,
        'headless': True,
        'log_level': 'INFO',
    }


def test_build_kwargs_omits_an_empty_browser_path():
    assert 'browser_path' not in build_kwargs(a_form())
    assert build_kwargs(a_form(browser_path='/usr/bin/google-chrome'))['browser_path'] == '/usr/bin/google-chrome'


def test_log_level_labels_map_to_library_levels():
    assert LOG_LEVEL_CHOICES == {'一般': 'INFO', '詳細（除錯用）': 'DEBUG'}


def test_validate_accepts_a_complete_form():
    assert validate(a_form()) is None


@pytest.mark.parametrize('overrides, expected', [
    ({'book_id': ''}, '請輸入書籍編號。'),
    ({'book_id': '  '}, '請輸入書籍編號。'),
    ({'book_id': '29a8'}, '書籍編號只能是數字。'),
    ({'chapter_delay': None}, '章節間隔秒數請填整數秒數。'),
    ({'page_delay': None}, '分頁間隔秒數請填整數秒數。'),
    ({'chapter_delay': -1}, '章節間隔秒數不能是負數。'),
    ({'page_delay': -1}, '分頁間隔秒數不能是負數。'),
    ({'output_dir': '/no/such/folder'}, '輸出資料夾不存在。'),
])
def test_validate_rejects_bad_input(overrides, expected):
    assert validate(a_form(**overrides)) == expected


def test_zero_delay_is_allowed():
    assert validate(a_form(chapter_delay=0, page_delay=0)) is None


def test_ensure_std_streams_replaces_missing_streams(monkeypatch):
    from linovelib2epub import gui

    monkeypatch.setattr(gui.sys, 'stdout', None)
    monkeypatch.setattr(gui.sys, 'stderr', None)

    gui.ensure_std_streams()

    assert gui.sys.stdout is not None and gui.sys.stderr is not None
    gui.sys.stdout.write('windowed builds must not crash on this')
