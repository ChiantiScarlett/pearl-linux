
from pearl import cgv, lotci
from pearl.core import Clip
import argparse
import sys
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed


class PearlError(Exception):
    "Custom Error for silencing Tracebacks"

    def __init__(self, msg):
        self.msg = msg
        # Set custom exception handler for Exception printouts
        sys.excepthook = self.Exception_Handler

    def Exception_Handler(self, exception_type, exception, tb):
        print('[PearlError] :: {}'.format(self.msg))

    def __str__(self):
        return "{}".format(self.msg)


def main(args=None):
    parser = argparse.ArgumentParser(
        description='Pearl'
    )
    parser.add_argument('-d', '--date',
                        help='date of the day (e.g. 3, 28, 30)',
                        required=False,
                        default=None)
    parser.add_argument('-w', '--weekday',
                        help='weekday of the day (e.g. mon, Saturday)',
                        required=False,
                        default=None)
    parser.add_argument('-t', '--title',
                        help='Filter results based on the keyword (e.g. 어벤져스)',
                        required=False,
                        default=None)

    args = vars(parser.parse_args(args))

    # If -w, validate, and convert weekday into date
    if args['weekday']:
        w_opts = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun',
                  'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                  'saturday', 'sunday']
        if args['weekday'].lower() not in w_opts:
            err = 'Invalid weekday option `{}`. '
            raise PearlError(err.format(args['weekday']))

        w_opts = {}
        date = datetime.now()
        for delta in range(7):
            w_opts[date.strftime('%a').lower()] = date.strftime("%d")
            date += timedelta(days=1)

        if args['weekday'].lower() not in w_opts:
            err = 'Data for the weekday `{}` is not available at the moment.'
            raise PearlError(err.format(args['weekday']))

    if args['date']:
        invalid = True
        if args.isnumeric():
            if (1 <= int(date) <= 31):
                invalid = False
        if invalid:
            err = 'Invalid date `{}`.'
            raise PearlError(err.format(args['date']))

    # If -w and -d are both on, validate if they indicates same date
    if args['date'] and args['weekday']:
        if int(args['date']) not in w_opts.values():
            err = '-d/--date and -w/--weekday indicate different date.'
            raise PearlError(err)

    # Run pearl functions with threading
    date = args['date']
    title = args['title']

    main_clip = Clip()
    pool = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        pool.append(executor.submit(cgv, '수원', date, title))
        pool.append(executor.submit(cgv, '북수원', date, title))
        pool.append(executor.submit(lotci, '수원', date, title))

    for clip in as_completed(pool):
        main_clip += clip.result()

    main_clip.show()


if __name__ == "__main__":
    main(sys.argv[1:])
