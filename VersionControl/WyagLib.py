import argparse
import sys

class wyag():

    def __init__(self):
        pass

    def processCLI(self, arg_list=None):
        parser = argparse.ArgumentParser(description='My Own Git')
        subparsers = parser.add_subparsers(help='Sub Commands')
        subparsers.required = True

        init_parser = subparsers.add_parser('init', help='Initialize Repo')
        init_parser.add_argument('path', help='Where to initialize repo')

        if arg_list is None or len(arg_list) < 1:
            parser.print_help()
            sys.exit(1)
    
        return vars(parser.parse_args(args=arg_list))

    def run(self):
        self.processCLI()
