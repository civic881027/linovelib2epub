"""Command-line entry point: ``linovelib2epub <book_id> [options]``."""
import argparse

from linovelib2epub import Linovelib2Epub, TargetSite


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='linovelib2epub',
        description='Crawl a light novel from the target site and convert it to EPUB.',
    )
    parser.add_argument('book_id', help='book id on the target site, e.g. 2978')
    parser.add_argument('--site', dest='target_site', default=TargetSite.LINOVELIB_MOBILE.value,
                        choices=[site.value for site in TargetSite],
                        help='target site (default: %(default)s)')
    parser.add_argument('--chapter-crawl-delay', type=int,
                        help='seconds to wait between chapters (required for linovelib sites)')
    parser.add_argument('--page-crawl-delay', type=int,
                        help='seconds to wait between pages (required for linovelib sites)')
    parser.add_argument('--divide-volume', action=argparse.BooleanOptionalAction,
                        help='write one epub per volume')
    parser.add_argument('--select-volume-mode', action=argparse.BooleanOptionalAction,
                        help='interactively pick which volumes to crawl')
    parser.add_argument('--has-illustration', action=argparse.BooleanOptionalAction,
                        help='download illustrations')
    parser.add_argument('--headless', action=argparse.BooleanOptionalAction,
                        help='run the browser headless')
    parser.add_argument('--browser-path', help='path to the Chromium-based browser binary')
    parser.add_argument('--log-level', help='DEBUG, INFO, WARNING or ERROR')
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    # Only forward options the user actually set so the library defaults stay in charge.
    kwargs = {key: value for key, value in vars(args).items() if value is not None}
    kwargs['target_site'] = TargetSite(kwargs['target_site'])
    try:
        crawler = Linovelib2Epub(**kwargs)
    except ValueError as error:  # the library validates argument combinations
        parser.error(str(error))
    crawler.run()


if __name__ == '__main__':
    main()
