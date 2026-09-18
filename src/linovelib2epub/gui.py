"""Local web front end: it serves one page on 127.0.0.1 and opens it in the browser, so the
Traditional Chinese labels are rendered with the browser's own fonts. Only the standard library
is used. Run it with `linovelib2epub-gui` or `python -m linovelib2epub.gui`."""
import json
import logging
import os
import secrets
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from linovelib2epub import Linovelib2Epub, TargetSite
from linovelib2epub.app import ensure_std_streams
from linovelib2epub import logger as logger_module
from linovelib2epub.spider.linovelib_spider import BaseLinovelibSpider
from linovelib2epub.utils import read_pkg_resource

# Field label -> value. The first site is the default: linovelib, PC theme, Traditional Chinese.
SITE_CHOICES = {
    '嗶哩輕小說（電腦版・繁體）': TargetSite.LINOVELIB_PC_TRADITIONAL,
    '嗶哩輕小說（電腦版・簡體）': TargetSite.LINOVELIB_PC,
    '嗶哩輕小說（手機版・繁體）': TargetSite.LINOVELIB_MOBILE_TRADITIONAL,
    '嗶哩輕小說（手機版・簡體）': TargetSite.LINOVELIB_MOBILE,
    '真白萌': TargetSite.MASIRO,
    '輕小說文庫': TargetSite.WENKU8,
}
DEFAULT_SITE_LABEL = '嗶哩輕小說（電腦版・繁體）'
LOG_LEVEL_CHOICES = {'一般': 'INFO', '詳細（除錯用）': 'DEBUG'}
DEFAULT_LOG_LEVEL_LABEL = '一般'
DEFAULT_DELAY = 5


def build_kwargs(form: dict) -> dict:
    """Translate the form into Linovelib2Epub keyword arguments."""
    kwargs = {
        'book_id': form['book_id'],
        'target_site': SITE_CHOICES[form['site_label']],
        'chapter_crawl_delay': form['chapter_delay'],
        'page_crawl_delay': form['page_delay'],
        'divide_volume': form['divide_volume'],
        'select_volume_mode': form['select_volume_mode'],
        'has_illustration': form['has_illustration'],
        'headless': form['headless'],
        'log_level': LOG_LEVEL_CHOICES[form['log_level_label']],
    }
    if form['browser_path']:
        kwargs['browser_path'] = form['browser_path']
    return kwargs


def validate(form: dict) -> str | None:
    """Return a Traditional Chinese error message, or None when the form is usable."""
    if form.get('site_label') not in SITE_CHOICES:
        return '請選擇小說網站。'
    if form.get('log_level_label') not in LOG_LEVEL_CHOICES:
        return '請選擇記錄詳細程度。'
    if not str(form['book_id']).strip():
        return '請輸入書籍編號。'
    if not str(form['book_id']).strip().isdigit():
        return '書籍編號只能是數字。'
    for value, name in ((form['chapter_delay'], '章節間隔秒數'), (form['page_delay'], '分頁間隔秒數')):
        if not isinstance(value, int):
            return f'{name}請填整數秒數。'
        if value < 0:
            return f'{name}不能是負數。'
    if not os.path.isdir(form['output_dir']):
        return '輸出資料夾不存在。'
    return None


class AppState:
    """Shared between the crawl worker and the HTTP handlers."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.lines: list = []
        self.running = False
        self.result: str | None = None  # empty on success, error text on failure, None while idle
        self.output_dir = os.getcwd()
        self.volume_titles: list | None = None  # set while the user is being asked
        self.volume_answer: list | None = None
        self.volume_answered = threading.Event()
        self.crawler = None  # the Linovelib2Epub instance, so its browser can be closed
        self.page_seen = False  # the page has polled at least once
        self.last_poll = 0.0
        self.shutting_down = False

    def mark_poll(self) -> None:
        with self.lock:
            self.page_seen = True
            self.last_poll = time.monotonic()

    def seconds_since_poll(self) -> float:
        with self.lock:
            return time.monotonic() - self.last_poll

    def add_line(self, line: str) -> None:
        with self.lock:
            self.lines.append(line)

    def snapshot(self, cursor: int) -> dict:
        with self.lock:
            cursor = max(0, min(cursor, len(self.lines)))
            return {
                'running': self.running,
                'result': self.result,
                'lines': self.lines[cursor:],
                'cursor': len(self.lines),
                'volumes': self.volume_titles,
                'outputDir': self.output_dir,
            }


class StateLogHandler(logging.Handler):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self.state.add_line(self.format(record))
        except Exception:
            pass


def page_is_gone(page_seen: bool, seconds_since_poll: float, grace: float = 12.0) -> bool:
    """The page polls every second. Only judge it gone after it has polled at least once, so a
    slow-starting browser is never mistaken for a closed one."""
    return page_seen and seconds_since_poll > grace


def close_browser(state: AppState) -> bool:
    """The library never closes the Chrome it starts, so closing it is left to the caller."""
    driver = getattr(getattr(state.crawler, '_spider', None), '_driver', None)
    if driver is None:
        return False
    try:
        driver.quit()
    except Exception:
        return False
    return True


def make_volume_selector(state: AppState):
    """Replaces the library's terminal prompt when 自選卷數 is ticked."""

    def select(catalog_list: list) -> list:
        with state.lock:
            state.volume_titles = [volume.volume_title for volume in catalog_list]
        state.volume_answer = None
        state.volume_answered.clear()
        state.volume_answered.wait()
        with state.lock:
            state.volume_titles = None
        if not state.volume_answer:
            raise RuntimeError('已取消：沒有選擇任何一卷。')
        return [catalog_list[row] for row in state.volume_answer]

    return select


def run_crawl(state: AppState, form: dict) -> None:
    try:
        # Everything the library writes (epub, images, logs) is relative to the working directory.
        os.chdir(form['output_dir'])
        logger_module.DEFAULT_LOG_FOLDER = os.path.join(form['output_dir'], 'logs')
        state.add_line(f'開始下載書籍 {form["book_id"]}，輸出到 {form["output_dir"]}')
        crawler = Linovelib2Epub(**build_kwargs(form))
        state.crawler = crawler
        crawler.run()
    except BaseException as error:  # noqa: BLE001 - any failure must reach the page
        message = str(error) or type(error).__name__
        state.add_line(f'失敗：{message}')
        with state.lock:
            state.result = message
    else:
        state.add_line('完成')
        with state.lock:
            state.result = ''
    finally:
        with state.lock:
            state.running = False
            state.volume_titles = None


def page_config(state: AppState) -> dict:
    return {
        'sites': list(SITE_CHOICES),
        'defaultSite': DEFAULT_SITE_LABEL,
        'logLevels': list(LOG_LEVEL_CHOICES),
        'defaultLogLevel': DEFAULT_LOG_LEVEL_LABEL,
        'defaultDelay': DEFAULT_DELAY,
        'outputDir': state.output_dir,
    }


def render_page(state: AppState) -> bytes:
    html = read_pkg_resource('web', 'index.html').decode('utf-8')
    return html.replace('__CONFIG__', json.dumps(page_config(state), ensure_ascii=False)).encode('utf-8')


class Handler(BaseHTTPRequestHandler):
    server_version = 'linovelib2epub'

    def log_message(self, *args) -> None:  # keep the console free for the crawl log
        pass

    # ---------- helpers ----------

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: dict, status: int = 200) -> None:
        self._send(status, json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                   'application/json; charset=utf-8')

    def _authorised(self, query: dict) -> bool:
        # The token stops any other page or process on this machine from driving the crawler.
        given = self.headers.get('X-Token') or (query.get('token') or [''])[0]
        return secrets.compare_digest(given, self.server.token)

    def _read_json(self) -> dict:
        length = int(self.headers.get('Content-Length') or 0)
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode('utf-8'))
        except ValueError:
            return {}

    # ---------- routes ----------

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        if not self._authorised(query):
            self._send(403, '403 forbidden'.encode('utf-8'), 'text/plain; charset=utf-8')
            return
        if parsed.path == '/':
            self._send(200, render_page(self.server.state), 'text/html; charset=utf-8')
        elif parsed.path == '/api/state':
            try:
                cursor = int((query.get('cursor') or ['0'])[0])
            except ValueError:
                cursor = 0
            self.server.state.mark_poll()
            self._send_json(self.server.state.snapshot(cursor))
        else:
            self._send(404, '404'.encode('utf-8'), 'text/plain; charset=utf-8')

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if not self._authorised(parse_qs(parsed.query)):
            self._send(403, '403 forbidden'.encode('utf-8'), 'text/plain; charset=utf-8')
            return
        state = self.server.state
        if parsed.path == '/api/start':
            self._start(state, self._read_json())
        elif parsed.path == '/api/volumes':
            state.volume_answer = self._read_json().get('selected') or []
            state.volume_answered.set()
            self._send_json({'ok': True})
        elif parsed.path == '/api/quit':
            self._send_json({'ok': True})
            stop_everything(self.server, '已停止，程式結束。')
        else:
            self._send(404, '404'.encode('utf-8'), 'text/plain; charset=utf-8')

    def _start(self, state: AppState, form: dict) -> None:
        with state.lock:
            if state.running:
                self._send_json({'ok': False, 'error': '已經在下載中。'}, 409)
                return
        error = validate(form)
        if error:
            self._send_json({'ok': False, 'error': error}, 400)
            return
        with state.lock:
            state.running = True
            state.result = None
            state.output_dir = form['output_dir']
        BaseLinovelibSpider._handle_select_volume = staticmethod(make_volume_selector(state))
        threading.Thread(target=run_crawl, args=(state, form), daemon=True).start()
        self._send_json({'ok': True})


def stop_everything(server, reason: str) -> None:
    """Close the crawl's browser, then stop serving. Crawl threads are daemons and die with the
    process, but the browser is a separate process and would otherwise be left behind."""
    state = server.state
    with state.lock:
        if state.shutting_down:
            return
        state.shutting_down = True
    state.add_line(reason)
    print(reason, flush=True)
    if close_browser(state):
        print('已關閉爬取用的瀏覽器。', flush=True)
    threading.Thread(target=server.shutdown, daemon=True).start()


def watch_page(server, grace: float = 12.0, interval: float = 1.0) -> None:
    """Quit once the page stops polling, so closing the browser tab does not leave this running."""
    state = server.state
    while not state.shutting_down:
        time.sleep(interval)
        if page_is_gone(state.page_seen, state.seconds_since_poll(), grace):
            stop_everything(server, '瀏覽器頁面已關閉，程式結束。')
            return


def serve(port: int = 0, open_browser: bool = True) -> None:
    state = AppState()
    handler = StateLogHandler(state)
    handler.setLevel(logging.DEBUG)
    # The library's loggers propagate to the root logger, so one handler here catches them all.
    logging.getLogger().addHandler(handler)

    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.state = state
    server.token = secrets.token_urlsafe(16)
    url = f'http://127.0.0.1:{server.server_port}/?token={server.token}'
    # flush: the launcher may be reading this through a pipe, and the server never exits on its own
    print(f'介面網址：{url}', flush=True)
    print('關閉這個視窗或按 Ctrl+C 可結束程式。', flush=True)
    if open_browser:
        webbrowser.open(url)
    threading.Thread(target=watch_page, args=(server,), daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        close_browser(state)
    finally:
        server.server_close()


def main(argv: list | None = None) -> None:
    ensure_std_streams()
    argv = sys.argv[1:] if argv is None else argv
    if '--check' in argv:  # bundle smoke test, no browser and no server
        print('\n'.join(SITE_CHOICES))
        # A packaged build must carry these; reading them here fails loudly if the spec drops one.
        for folder, name in (('web', 'index.html'), ('styles', 'chapter.css'),
                             ('styles', 'cover.css'), ('styles', 'nav.css')):
            print(f'resource ok: {folder}/{name} ({len(read_pkg_resource(folder, name))} bytes)')
        return
    port = 0
    if '--port' in argv:
        port = int(argv[argv.index('--port') + 1])
    serve(port=port, open_browser='--no-browser' not in argv)


if __name__ == '__main__':
    main()
