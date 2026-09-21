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
    assert page_is_gone(page_seen=False, seconds_since_poll=9999.0, grace=60.0) is False


def test_an_idle_page_is_gone_after_a_long_silence():
    from linovelib2epub.gui import page_is_gone

    assert page_is_gone(page_seen=True, seconds_since_poll=60.5, running=False, grace=60.0) is True


def test_page_is_not_gone_while_it_keeps_polling():
    from linovelib2epub.gui import page_is_gone

    assert page_is_gone(page_seen=True, seconds_since_poll=1.0, grace=60.0) is False
    # a page reload pauses polling briefly and must not kill the program
    assert page_is_gone(page_seen=True, seconds_since_poll=60.0, grace=60.0) is False


def test_a_silent_page_never_ends_a_running_download():
    from linovelib2epub.gui import page_is_gone

    # Chrome discards background tabs; the download must survive that
    assert page_is_gone(page_seen=True, seconds_since_poll=9999.0, running=True, grace=60.0) is False


def test_a_goodbye_counts_once_the_grace_has_passed_without_a_new_poll():
    from linovelib2epub.gui import page_said_bye

    assert page_said_bye(bye_at=100.0, last_poll=99.5, now=103.5, grace=3.0) is True
    assert page_said_bye(bye_at=100.0, last_poll=99.5, now=103.0, grace=3.0) is False  # boundary
    assert page_said_bye(bye_at=100.0, last_poll=99.5, now=101.0, grace=3.0) is False


def test_a_reloaded_page_cancels_the_goodbye():
    from linovelib2epub.gui import page_said_bye

    # the reload unloads the old page (goodbye) and the new one polls again within the grace
    assert page_said_bye(bye_at=100.0, last_poll=101.0, now=110.0, grace=3.0) is False


def test_no_goodbye_yet_means_nothing_to_act_on():
    from linovelib2epub.gui import page_said_bye

    assert page_said_bye(bye_at=0.0, last_poll=0.0, now=9999.0, grace=3.0) is False


def test_the_watchdog_quits_after_a_goodbye_but_not_while_downloading(monkeypatch):
    import threading

    from linovelib2epub import gui

    class FakeServer:
        def __init__(self):
            self.state = gui.AppState()
            self.stopped_for = []

    server = FakeServer()
    monkeypatch.setattr(gui, 'stop_everything', lambda srv, reason: srv.stopped_for.append(reason))
    server.state.mark_poll()
    server.state.running = True
    server.state.last_poll -= 9999  # a discarded tab: silent for ages while downloading

    watcher = threading.Thread(daemon=True, target=gui.watch_page, args=(server, 60.0, 0.01))
    watcher.start()
    time.sleep(0.1)
    assert server.stopped_for == []  # silence alone does not end a download

    server.state.mark_bye()
    server.state.bye_at -= 5  # the goodbye is older than its grace and no poll followed
    watcher.join(timeout=2)
    assert server.stopped_for == ['瀏覽器頁面已關閉，程式結束。']


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


# ---------- the volume question: an answer names the question it answers ----------

def wait_for_question(state, timeout=2.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if state.snapshot(0)['volumes'] is not None:
            return
        time.sleep(0.01)
    raise AssertionError('the volume question never appeared')


def a_catalog():
    from types import SimpleNamespace

    return [SimpleNamespace(volume_title='v1', chapters=[1]),
            SimpleNamespace(volume_title='v2', chapters=[2, 3])]


def test_only_an_answer_to_the_current_question_counts():
    import threading

    from linovelib2epub.gui import AppState, answer_volumes, make_volume_selector

    state = AppState()
    chosen = []
    worker = threading.Thread(daemon=True, target=lambda: chosen.append(make_volume_selector(state)(a_catalog())))
    worker.start()
    wait_for_question(state)
    assert state.snapshot(0)['volumeRequest'] == 1

    # a stale page (or a double click on the re-shown panel) answers an earlier question
    assert answer_volumes(state, {'selected': [], 'request': 0}) is False
    assert worker.is_alive()

    assert answer_volumes(state, {'selected': [1], 'request': 1}) is True
    assert state.snapshot(0)['volumes'] is None  # cleared for the next poll, not only by the worker
    worker.join(timeout=2)
    assert [volume.volume_title for volume in chosen[0]] == ['v2']
    assert state.progress()['total'] == 2


def test_an_answer_when_nothing_is_asked_is_ignored():
    from linovelib2epub.gui import AppState, answer_volumes

    state = AppState()

    assert answer_volumes(state, {'selected': [0], 'request': 0}) is False
    assert not state.volume_answered.is_set()


def test_choosing_nothing_cancels_the_run():
    import threading

    from linovelib2epub.gui import AppState, answer_volumes, make_volume_selector

    state = AppState()
    errors = []

    def run():
        try:
            make_volume_selector(state)(a_catalog())
        except RuntimeError as error:
            errors.append(str(error))

    worker = threading.Thread(daemon=True, target=run)
    worker.start()
    wait_for_question(state)
    answer_volumes(state, {'selected': [], 'request': 1})
    worker.join(timeout=2)

    assert errors == ['已取消：沒有選擇任何一卷。']


# ---------- stopping the download without ending the program ----------

def test_stop_does_nothing_while_no_download_runs():
    from linovelib2epub.gui import AppState, request_stop

    state = AppState()

    assert request_stop(state) is False
    assert not state.stop_event.is_set()


def test_stop_sets_the_signal_the_crawl_watches():
    from linovelib2epub.gui import AppState, request_stop

    state = AppState()
    state.running = True

    assert request_stop(state) is True
    assert state.stop_event.is_set()


def test_stop_wakes_a_crawl_waiting_for_the_volume_choice():
    import threading

    from linovelib2epub.exceptions import CrawlStopped
    from linovelib2epub.gui import AppState, make_volume_selector, request_stop

    state = AppState()
    state.running = True
    outcome = []

    def run():
        try:
            make_volume_selector(state)(a_catalog())
        except CrawlStopped:
            outcome.append('stopped')

    worker = threading.Thread(daemon=True, target=run)
    worker.start()
    wait_for_question(state)
    request_stop(state)
    worker.join(timeout=2)

    assert outcome == ['stopped']
    assert state.snapshot(0)['volumes'] is None


def test_a_stop_requested_before_the_question_is_not_missed():
    from linovelib2epub.exceptions import CrawlStopped
    from linovelib2epub.gui import AppState, make_volume_selector, request_stop

    state = AppState()
    state.running = True
    request_stop(state)

    with pytest.raises(CrawlStopped):
        make_volume_selector(state)(a_catalog())


class FakeCrawler:
    outcome = None  # an exception to raise from run(), or None

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.closed = False

    def run(self):
        if self.outcome is not None:
            raise self.outcome

    def close(self):
        self.closed = True


def a_crawl(monkeypatch, tmp_path, outcome):
    from linovelib2epub import gui

    monkeypatch.chdir(tmp_path)  # run_crawl changes directory to the output folder
    monkeypatch.setattr(gui.logger_module, 'DEFAULT_LOG_FOLDER', gui.logger_module.DEFAULT_LOG_FOLDER)
    monkeypatch.setattr(gui.linovel_module, 'Confirm', gui.linovel_module.Confirm)
    monkeypatch.setattr(FakeCrawler, 'outcome', outcome)
    monkeypatch.setattr(gui, 'Linovelib2Epub', FakeCrawler)
    state = gui.AppState()
    state.running = True
    gui.run_crawl(state, a_form(output_dir=str(tmp_path)))
    return state


def test_a_stopped_download_is_reported_as_stopped_not_failed(monkeypatch, tmp_path):
    from linovelib2epub.exceptions import CrawlStopped

    state = a_crawl(monkeypatch, tmp_path, CrawlStopped())

    snapshot = state.snapshot(0)
    assert snapshot['stopped'] is True
    assert snapshot['running'] is False
    assert snapshot['result'] == '已停止下載。'
    assert '已停止下載。' in snapshot['lines']


def test_the_crawl_gets_the_stop_signal_of_this_run(monkeypatch, tmp_path):
    state = a_crawl(monkeypatch, tmp_path, None)

    assert state.crawler.kwargs['stop_event'] is state.stop_event
    assert state.snapshot(0)['result'] == ''


def test_a_failure_is_still_a_failure(monkeypatch, tmp_path):
    state = a_crawl(monkeypatch, tmp_path, RuntimeError('boom'))

    snapshot = state.snapshot(0)
    assert snapshot['stopped'] is False
    assert snapshot['result'] == 'boom'
