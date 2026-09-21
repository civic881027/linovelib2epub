import os
import time

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
        'resume': True,
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
        'resume': True,
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
    from linovelib2epub import app

    monkeypatch.setattr(app.sys, 'stdout', None)
    monkeypatch.setattr(app.sys, 'stderr', None)

    app.ensure_std_streams()

    assert app.sys.stdout is not None and app.sys.stderr is not None
    app.sys.stdout.write('windowed builds must not crash on this')


def test_ensure_std_streams_switches_the_console_to_utf8(monkeypatch):
    """Redirected output on Windows defaults to the ANSI code page, which cannot encode Chinese."""
    from unittest.mock import Mock

    from linovelib2epub import app

    stdout, stderr = Mock(), Mock()
    monkeypatch.setattr(app.sys, 'stdout', stdout)
    monkeypatch.setattr(app.sys, 'stderr', stderr)

    app.ensure_std_streams()

    stdout.reconfigure.assert_called_once_with(encoding='utf-8', errors='replace')
    stderr.reconfigure.assert_called_once_with(encoding='utf-8', errors='replace')


def test_ensure_std_streams_tolerates_a_stream_that_cannot_be_reconfigured(monkeypatch):
    import io

    from linovelib2epub import app

    class Stubborn(io.StringIO):
        def reconfigure(self, **kwargs):
            raise OSError('not a real console')

    monkeypatch.setattr(app.sys, 'stdout', Stubborn())
    monkeypatch.setattr(app.sys, 'stderr', Stubborn())

    app.ensure_std_streams()  # must not raise

    app.sys.stdout.write('嗶哩輕小說')


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


def test_close_browser_releases_the_crawlers_browser():
    from unittest.mock import Mock

    from linovelib2epub.gui import AppState, close_browser

    state = AppState()
    state.crawler = Mock(_spider=Mock(_driver=Mock()))

    assert close_browser(state) is True
    state.crawler.close.assert_called_once_with()


def test_close_browser_is_a_no_op_before_a_crawl_starts():
    from linovelib2epub.gui import AppState, close_browser

    assert close_browser(AppState()) is False


def test_close_browser_survives_a_browser_that_refuses_to_quit():
    from unittest.mock import Mock

    from linovelib2epub.gui import AppState, close_browser

    state = AppState()
    state.crawler = Mock(_spider=Mock(_driver=Mock()), close=Mock(side_effect=OSError('browser gone')))

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


def test_no_estimate_before_a_chapter_finishes():
    from linovelib2epub.gui import estimate_remaining

    assert estimate_remaining(done=0, total=120, elapsed=30.0) is None
    assert estimate_remaining(done=5, total=0, elapsed=30.0) is None
    assert estimate_remaining(done=5, total=120, elapsed=0.0) is None


def test_no_estimate_once_every_chapter_is_done():
    from linovelib2epub.gui import estimate_remaining

    assert estimate_remaining(done=120, total=120, elapsed=600.0) is None


def test_estimate_scales_with_the_measured_rate():
    from linovelib2epub.gui import estimate_remaining

    # 10 chapters took 100s, so each takes 10s, and 90 remain
    assert estimate_remaining(done=10, total=100, elapsed=100.0) == 900.0


def test_only_the_chapter_start_line_counts_as_progress():
    from linovelib2epub.gui import is_chapter_start

    assert is_chapter_start('chapter : 5 帝都') is True
    # the library logs this again when it renames a chapter, which would double count
    assert is_chapter_start('chapter : [5 帝都] New Title= [5 帝都 (1)]') is False
    assert is_chapter_start('volume: 第一卷') is False
    assert is_chapter_start('page https://example.invalid/1.html => ok.') is False


def test_total_chapters_comes_from_the_catalog():
    from types import SimpleNamespace

    from linovelib2epub.gui import count_chapters

    catalog = [SimpleNamespace(chapters=[1, 2, 3]), SimpleNamespace(chapters=[4, 5])]
    assert count_chapters(catalog) == 5
    assert count_chapters([]) == 0


def test_state_reports_progress_from_the_chapter_log():
    from linovelib2epub.gui import AppState

    state = AppState()
    state.set_total_chapters(10)
    for _ in range(4):
        state.note_chapter_started()
    # pin the clock: on a coarse one the four calls above can read as no time at all
    state.first_chapter_at = time.monotonic() - 30

    progress = state.progress()

    # the fourth chapter is still being fetched, so three are done
    assert progress['done'] == 3
    assert progress['total'] == 10
    assert progress['etaSeconds'] == pytest.approx(30 / 3 * 7, abs=1)


def test_no_estimate_until_measurable_time_has_passed(monkeypatch):
    from linovelib2epub import gui

    # freeze the clock: Windows reads coarsely enough that two calls can show no elapsed time,
    # and that must not turn into an estimate rather than "not yet known"
    monkeypatch.setattr(gui.time, 'monotonic', lambda: 1000.0)
    state = gui.AppState()
    state.set_total_chapters(10)
    state.note_chapter_started()
    state.note_chapter_started()

    assert state.progress()['etaSeconds'] is None


def test_progress_resets_between_runs():
    from linovelib2epub.gui import AppState

    state = AppState()
    state.set_total_chapters(10)
    state.note_chapter_started()

    state.reset_progress()

    assert state.progress() == {'done': 0, 'total': 0, 'etaSeconds': None}


def test_resume_reaches_the_library():
    assert build_kwargs(a_form(resume=True))['resume'] is True
    assert build_kwargs(a_form(resume=False))['resume'] is False


def test_validate_requires_an_explicit_resume_choice():
    form = a_form()
    del form['resume']

    assert validate(form) == '請指定要沿用還是捨棄上次的進度。'


def test_fixed_answer_replaces_the_terminal_prompt():
    from linovelib2epub.gui import FixedAnswer

    # the library calls Confirm.ask(message); it must never reach stdin
    assert FixedAnswer(True).ask('The last unfinished work was detected, continue?') is True
    assert FixedAnswer(False).ask('anything', default=True) is False
