"""Single entry point for the packaged executable.

Double-clicking it passes no arguments, which opens the web interface. Anything else is treated
as a command line, so the executable serves both kinds of user from one file."""
import sys


def route(argv: list) -> tuple:
    """Return ('gui' | 'cli', arguments) for the given command line."""
    if not argv:
        return 'gui', []
    if argv[0] == 'gui':
        return 'gui', argv[1:]
    return 'cli', argv


def main(argv: list | None = None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    target, arguments = route(argv)
    if target == 'gui':
        from linovelib2epub.gui import main as gui_main
        gui_main(arguments)
    else:
        from linovelib2epub.cli import main as cli_main
        cli_main(arguments)


if __name__ == '__main__':
    main()
