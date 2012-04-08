#!/usr/bin/env python
from __future__ import print_function
import argparse
import os
import sys


def print_list(*l):
    for x in l:
        print(x)

class File(object):
    def __init__(self, filename, link_filename, repo_filename, status):
        self.filename = filename
        self.link_filename = link_filename
        self.repo_filename = repo_filename
        self.status = status

    def __str__(self):
        return '{0:<4} {1}'.format(self.status, self.filename)

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

    def get_files(self):
        files = []
        for fn in os.listdir(self.path):
            file_status = ''
            file_basename = os.path.basename(fn)

            # check if the file is .hg, .git or .bzr and skip those
            if file_basename == self.get_type():
                continue
            repo_file = os.path.abspath(os.path.join(self.path, fn))
            home_file = os.path.abspath(os.path.join(os.path.expanduser('~'), fn))

            if os.path.exists(home_file):
                if os.path.islink(home_file):
                    file_status = 'ok' # linked
                else:
                    file_status = 'C' # there is file in home dir, but it is not the same as one in repo
            else:
                file_status = '!' # there is not file in home dir, missing or deleted
            files.append(File(file_basename, home_file, repo_file, file_status))
        return files

class Command(object):
    def __init__(self, repo):
        self.repo = repo

    @classmethod
    def is_valid(cls, command):
        return command in ('push', 'pull', 'status', 'link', 'unlink', ) 

    def push(self, *args):
        print_list(*args)

    def pull(self, *args):
        print_list(*args)

    def status(self, *args):
        for x in self.repo.get_files():
            print(x)

    def link(self, *args):
        print_list(*args)
        for x in [x for x in self.repo.get_files() if x.status == '!']:
            os.symlink(x.repo_filename, x.link_filename)
            print(u'{0} -> {1}'.format(x.link_filename, x.repo_filename))

    def unlink(self, *args):
        for x in [x for x in self.repo.get_files() if x.status == 'ok']:
            os.unlink(x.link_filename)
            print(u'{0} unlinked'.format(x.link_filename))

def get_parser():
    parser = argparse.ArgumentParser(description='dots.py - DO your doTfileS')
    parser.add_argument('command')
    parser.add_argument('repository')
    parser.add_argument('options', nargs='*')
    parser.add_argument('--debug', action='store_true', help='Turn on debug mode')

    return parser

def show_error(msg):
    print(msg)
    sys.exit(1)

if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    if not Command.is_valid(args.command):
        show_error('{0} is not a valid command'.format(args.command))
    if not os.path.exists(args.repository):
        show_error('{0} is not a repository'.format(args.repository))

    command = Command(Repository(args.repository))
    if args.debug:
        print('command:', args.command)
        print('repo:', args.repository)

    if args.options:
        print('options:', list(args.options))

    getattr(command, args.command)(*args.options)

