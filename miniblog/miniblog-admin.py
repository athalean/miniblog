import os
import sys
import argparse

from builder import build_site
from server import run_server


def build(folder):
    build_site(os.path.join(folder, 'out'), os.path.join(folder, 'content'),
               os.path.join(folder, 'templates'))


def serve(folder):
    run_server(os.path.join(folder, 'content'), os.path.join(folder, 'templates'), os.path.join(
        folder, 'media'))


def create():
    pass


def run_command(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='A static website generator')
    parser.add_argument('action', choices=['build', 'serve'])

    args = parser.parse_args()
    if args.action == 'build':
        build(os.getcwd())
    elif args.action == 'serve':
        serve(os.getcwd())


if __name__ == '__main__':
    run_command()