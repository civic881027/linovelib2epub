"""Single entry point for the packaged executable.

Double-clicking it passes no arguments, which opens the web interface. Anything else is treated
as a command line, so the executable serves both kinds of user from one file."""
import os
import sys


def ensure_std_streams() -> None:
    """Make stdout/stderr safe for Traditional Chinese.

    A windowed build has no console at all, so the streams are None and the library's rich log
    handler would fail on the first message. When the output is redirected on Windows the streams
    default to the ANSI code page instead of UTF-8, and printing Chinese raises UnicodeEncodeError.
    """
    for name in ('stdout', 'stderr'):
        stream = getattr(sys, name, None)
        if stream is None:
            setattr(sys, name, open(os.devnull, 'w', encoding='utf-8'))
            continue
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError, OSError):
            pass  # already unicode-safe, or not a reconfigurable text stream


def route(argv: list) -> tuple:
    """Return ('gui' | 'cli', arguments) for the given command line."""
    if not argv:
        return 'gui', []
    if argv[0] == 'gui':
        return 'gui', argv[1:]
    return 'cli', argv


def main(argv: list | None = None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    ensure_std_streams()  # before anything can print a Chinese book title
    target, arguments = route(argv)
    if target == 'gui':
        from linovelib2epub.gui import main as gui_main
        gui_main(arguments)
    else:
        from linovelib2epub.cli import main as cli_main
        cli_main(arguments)


if __name__ == '__main__':
    main()
