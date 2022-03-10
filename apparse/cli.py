import argparse
import sys
import traceback

from ._version import __version__
from . import parse_iw_device, parse_iw_station, parse_iwinfo_device, parse_iwinfo_station


def cli():

    def format_exc(exc, tb=False):
        if str(exc):
            msg = f'{type(exc).__name__}: {exc}'
            if tb:
                return f'{msg}\n{traceback.format_exc()}'
            return msg
        return f'{type(exc).__name__}: {traceback.format_exc()}'

    def error(msg, exc=None, tb=False):
        if exc:
            print(f'{msg}: {format_exc(exc, tb)}', file=sys.stderr)
        else:
            print(msg, file=sys.stderr)
        sys.exit(1)

    class HelpFormatter(argparse.HelpFormatter):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, max_help_position=32, **kwargs)

        def _format_action_invocation(self, action):
            if not action.option_strings or action.nargs == 0:
                return super()._format_action_invocation(action)
            default = self._get_default_metavar_for_optional(action)
            args_string = self._format_args(action, default)
            return f"{', '.join(action.option_strings)} {args_string}"

    parser = argparse.ArgumentParser(formatter_class=HelpFormatter)
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=f'ap-parse {__version__}'
    )
    parser.add_argument(
        'format',
        choices=('iw', 'iwinfo'),
        help='Format of input data (iw, iwinfo)',
        metavar='<format>'
    )
    parser.add_argument(
        'type',
        choices=('device', 'station'),
        help='Type of input data (device, station)',
        metavar='<type>'
    )
    args = parser.parse_args()

    if args.format == 'iw':
        if args.type == 'device':
            parse_func = parse_iw_device
        else:
            parse_func = parse_iw_station
    else:
        if args.type == 'device':
            parse_func = parse_iwinfo_device
        else:
            parse_func = parse_iwinfo_station

    try:
        print(parse_func(sys.stdin.read()))
    except ValueError as e:
        error('Error parsing data', e)


def main():
    try:
        cli()
    except KeyboardInterrupt:
        print('Interrupted', file=sys.stderr)
        sys.exit(1)
