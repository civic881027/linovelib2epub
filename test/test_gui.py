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


def test_page_is_gone_only_after_the_page_has_polled_once():
    from linovelib2epub.gui import page_is_gone

    # a slow-starting browser has not polled yet, so it is never judged gone
    assert page_is_gone(page_seen=False, seconds_since_poll=9999.0, grace=12.0) is False


def test_page_is_gone_when_polling_stops():
    from linovelib2epub.gui import page_is_gone

    assert page_is_gone(page_seen=True, seconds_since_poll=12.5, grace=12.0) is True


def test_page_is_not_gone_while_it_keeps_polling():
    from linovelib2epub.gui import page_is_gone

    assert page_is_gone(page_seen=True, seconds_since_poll=1.0, grace=12.0) is False
    # a page reload pauses polling briefly and must not kill the program
    assert page_is_gone(page_seen=True, seconds_since_poll=12.0, grace=12.0) is False


def test_close_browser_quits_the_crawlers_driver():
    from unittest.mock import Mock

    from linovelib2epub.gui import AppState, close_browser

    driver = Mock()
    state = AppState()
    state.crawler = Mock(_spider=Mock(_driver=driver))

    assert close_browser(state) is True
    driver.quit.assert_called_once_with()


def test_close_browser_is_a_no_op_before_a_crawl_starts():
    from linovelib2epub.gui import AppState, close_browser

    assert close_browser(AppState()) is False


def test_close_browser_survives_a_driver_that_refuses_to_quit():
    from unittest.mock import Mock

    from linovelib2epub.gui import AppState, close_browser

    state = AppState()
    state.crawler = Mock(_spider=Mock(_driver=Mock(quit=Mock(side_effect=OSError('browser gone')))))

    assert close_browser(state) is False


def test_double_click_with_no_arguments_opens_the_web_interface():
    from linovelib2epub.app import route

    assert route([]) == ('gui', [])


def test_gui_subcommand_passes_its_own_flags_through():
    from linovelib2epub.app import route

    assert route(['gui', '--port', '8000']) == ('gui', ['--port', '8000'])


def test_any_other_argument_goes_to_the_command_line():
    from linovelib2epub.app import route

    assert route(['2978', '--site', 'linovelib_pc']) == ('cli', ['2978', '--site', 'linovelib_pc'])
    assert route(['--help']) == ('cli', ['--help'])
