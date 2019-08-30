#!/usr/bin/env python3

import sys
import os


def _process(data: str):
    print(data)


def main():
    piped = not sys.stdin.isatty()  # read from input only when piped to
    if piped:
        _process(sys.stdin.read())
    else:
        print("E: only data from stdin supported")
        exit(1)


if __name__ == '__main__':
    main()
