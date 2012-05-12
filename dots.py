#!/usr/bin/env python
from __future__ import print_function
import argparse
import os
import sys
import subprocess


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
        self.config_file = os.path.abspath(os.path.join(self.path, '.dots'))
        self._set_config()

    def _set_config(self):
        import json
        self.target_dir = os.path.abspath(os.path.expanduser('~'))
        if os.path.exists(self.config_file):
            config = json.loads(open(self.config_file).read())
            self.target_dir = os.path.expanduser(config['target'])

    def get_dvcs(self):
        """ returns git, hg or None for given repository """
        for x in ('.git', '.hg', ):
            if os.path.isdir(os.path.join(self.path, x)):
                return x
        return None

    def should_skip_file(self, filename):
        """ files that should be skipped are repository directory and 
            .dots which is config file for dots.py
        """
        files_to_skip = [self.get_dvcs()]
        files_to_skip.append('.dots')
        return filename in files_to_skip

    def get_files(self):
        files = []
        for fn in os.listdir(self.path):
            file_status = ''
            file_basename = os.path.basename(fn)

            if self.should_skip_file(file_basename):
                continue
            source_file = os.path.abspath(os.path.join(self.path, fn))
            target_file = os.path.abspath(os.path.join(self.target_dir, fn))

            if os.path.exists(target_file):
                if os.path.islink(target_file):
                    file_status = 'ok' # linked
                else:
                    file_status = 'C' # there is file in home dir, but it is not the same as one in repo
            else:
                file_status = '!' # there is not file in home dir, missing or deleted
            files.append(File(file_basename, target_file, source_file, file_status))
        return files

class HgRepository(Repository):
    def push(self, *args):
        subprocess.call(['hg', 'add'])
        subprocess.call(['hg', 'commit', '-m', '.'])
        subprocess.call(['hg', 'push'])

    def pull(self, *args):
        subprocess.call(['hg', 'pull', '-u'])

class GitRepository(Repository):
    def push(self, *args):
        subprocess.call(['git', 'commit', '-am', '.'])
        subprocess.call(['git', 'push', 'origin', 'master'])

    def pull(self, *args):
        subprocess.call(['git', 'pull'])

class Command(object):
    def __init__(self, repo):
        self.repo = repo

    @classmethod
    def is_valid(cls, command):
        return command in ('push', 'pull', 'list', 'link', 'unlink', ) 

    def list(self, *args):
        for x in self.repo.get_files():
            print(x)

    def push(self, *args):
        os.chdir(self.repo.path)
        self.repo.push(*args)

    def pull(self, *args):
        os.chdir(self.repo.path)
        self.repo.pull(*args)

    def link(self, *args):
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

    r = Repository(args.repository).get_dvcs()[1:].capitalize()
    RepositoryClass = globals()[r+'Repository']
    command = Command(RepositoryClass(args.repository))
    if args.debug:
        print('command:', args.command)
        print('repo:', args.repository)

    if args.options:
        print('options:', list(args.options))

    getattr(command, args.command)(*args.options)

