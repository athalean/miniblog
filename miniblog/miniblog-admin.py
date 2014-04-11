import os
import sys
import argparse

from server import run_server


def build():
    pass


def serve(folder):
    run_server(os.path.join(folder,'content'), os.path.join(folder,'templates'))


def create():
    pass


def run_command(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='A static website generator')
    parser.add_argument('action', choices=['build', 'serve'])

    args = parser.parse_args()
    if args.action == 'build':
        build()
    if args.action == 'serve':
        serve(os.getcwd())


if __name__ == '__main__':
    run_command()