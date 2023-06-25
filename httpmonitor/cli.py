import argparse

from .errors import SetupRequiredException
from .scheduler import Scheduler
from .setup import setup

class CommandHandler:

    @staticmethod
    def run(args):
        if args.setup:
            try:
                setup()
            except Exception as e:
                print(str(e))
        else:
            try:
                scheduler = Scheduler(from_file="from_file" in args)
                scheduler.schedule_jobs()
                scheduler.scan_process.run()
            except SetupRequiredException as e:
                print(str(e))


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from_file",
                        help="""
                        By default httpmonitor loads jobs from the database.
                        With this flag the scripts loads the jobs from the predefined 'job.json' and stores them in the database
                        """,
                        action='store_true')
    parser.add_argument("--setup", help="Run setup initialization", action='store_true')
    args = parser.parse_args()

    CommandHandler.run(args)
