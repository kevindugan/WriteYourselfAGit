import argparse
import sys, os
from VersionControl import GitRepository
from VersionControl import GitObjectFactory

class wyag(object):

    def __init__(self):
        pass

    def processCLI(self, arg_list=None):
        parser = argparse.ArgumentParser(description='My Own Git')
        subparsers = parser.add_subparsers(help='Sub Commands', dest='command')
        subparsers.required = True

        init_parser = subparsers.add_parser('init', help='Initialize Repo')
        init_parser.add_argument('path', help='Where to initialize repo')

        hash_obj_parser = subparsers.add_parser('hash-object', help='Hash file into object type')
        hash_obj_parser.add_argument('path', help='Path to file')
        hash_obj_parser.add_argument('-w', help='Actually write object file', dest='write_obj', action='store_true')
        hash_obj_parser.add_argument('-t', help='Type of Object', dest='object_type', choices=['blob'], default='blob')

        cat_file_parser = subparsers.add_parser('cat-file', help='Output contents of object')
        cat_file_parser.add_argument('hash', help='Hash of object')
        cat_file_parser.add_argument('-t', help="Type of Object", dest="object_type", choices=['blob'], default='blob')

        if arg_list is not None and len(arg_list) < 1:
            parser.print_help()
            sys.exit(1)
    
        return vars(parser.parse_args(args=arg_list))

    def run(self, arg_list=None):
        cli_args = self.processCLI(arg_list)

        if "command" not in cli_args:
            return

        if cli_args["command"] == "init":
            repo = GitRepository.GitRepository(cli_args['path'])
            repo.initializeGitDir()

        elif cli_args["command"] == "hash-object":
            repo = GitRepository.GitRepository.find_repo(cli_args['path'])
            fileContents = ""
            with open(cli_args['path']) as f:
                fileContents = f.read()
            obj = GitObjectFactory.GitObjectFactory.factory(cli_args["object_type"], repo, fileContents)
            print(obj.create_object(cli_args['write_obj']))

        elif cli_args["command"] == "cat-file":
            repo = GitRepository.GitRepository.find_repo(os.getcwd())
            obj = GitObjectFactory.GitObjectFactory.factory(cli_args["object_type"], repo)
            print(obj.read_object(cli_args['hash']).serializeData(), end='')