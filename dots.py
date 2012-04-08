#!/usr/bin/env python
import argparse
import os


def print_list(*l):
    for x in l:
        print x

class Repository(object):
    def __init__(self, path):
        self.path = os.path.abspath(path)

    def get_type(self):
        """ returns git, hg, bzr or None for given repository """
        for x in ('.git', '.hg', '.bzr', ):
            r = os.path.join(self.path, x)
            if os.path.isdir(r):
                return x
        return None

class Command(object):
    @classmethod
    def is_valid(cls, command):
        return command in ('clone', 'push', 'pull', 'status', 'link', 'unlink', ) 

    def clone(self, repo, *args):
        print repo
        print_list(*args)

    def push(self, repo, *args):
        print_list(*args)

    def pull(self, repo, *args):
        print_list(*args)

    def status(self, repo, *args):
        #print_list(*args)
        for fn in os.listdir(repo.path):
            file_status = ''
            file_basename = os.path.basename(fn)

            # check if the file is .hg, .git or .bzr and skip those
            if file_basename == repo.get_type():
                continue
            repo_file = os.path.abspath(os.path.join(repo.path, fn))
            home_file = os.path.abspath(os.path.join(os.path.expanduser('~'), fn))

            if os.path.exists(home_file):
                if os.path.islink(home_file):
                    file_status = 'ok' # linked
                else:
                    file_status = 'C ' # there is file in home dir, but it is not the same as one in repo
            else:
                file_status = 'D ' # there is not file in home dir, missing or deleted
            print '{0} {1}'.format(file_status, file_basename)

    def link(self, repo, *args):
        print_list(*args)

def main():
    parser = argparse.ArgumentParser(description='dots.py - DO your doTfileS')
    parser.add_argument('command')
    parser.add_argument('repository')
    parser.add_argument('options', nargs='*')
    parser.add_argument('--debug', action='store_true', help='Turn on debug mode')

    return parser

def test_parser(args):
    print args.command
    print args.repository

if __name__ == '__main__':
    parser = main()
    args = parser.parse_args()

    assert Command.is_valid(args.command)
    assert os.path.exists(args.repository)

    c = Command()
    if args.debug:
        print 'command: ', args.command
        print 'repo: ', args.repository

    if args.options:
        print list(args.options)
    getattr(c, args.command)(Repository(args.repository), *args.options)

    #test_parser(args)

