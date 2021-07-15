#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Jānis Zuters

from __future__ import unicode_literals, division

import sys
import codecs
import argparse

from io import open
argparse.open = open

from prpe import unprocess_prpe

def create_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="make first symbol uppercase if word follows the marker")
    parser.add_argument(
        '--input', '-i', type=argparse.FileType('r'), default=sys.stdin,
        metavar='PATH',
        help="Input file (default: standard input).")
    parser.add_argument(
        '--output', '-o', type=argparse.FileType('w'), default=sys.stdout,
        metavar='PATH',
        help="Output file (default: standard output)")
    parser.add_argument(
        '--marker1', '-m', type=str, default='9474', metavar='STR',
        help="Segmentation marker (default: '%(default)s'))")
    parser.add_argument(
        '--marker2', '-n', type=str, default='9553', metavar='STR',
        help="Uppercase marker (default: '%(default)s'))")
    parser.add_argument(
        '--mode', '-d', type=int, default=1,
        help="Marking mode of segmentation")
    return parser

if __name__ == '__main__':

    # python 2/3 compatibility
    if sys.version_info < (3, 0):
        sys.stderr = codecs.getwriter('UTF-8')(sys.stderr)
        sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)
        sys.stdin = codecs.getreader('UTF-8')(sys.stdin)
    else:
        sys.stderr = codecs.getwriter('UTF-8')(sys.stderr.buffer)
        sys.stdout = codecs.getwriter('UTF-8')(sys.stdout.buffer)
        sys.stdin = codecs.getreader('UTF-8')(sys.stdin.buffer)

    parser = create_parser()
    args = parser.parse_args()

    # read/write files as UTF-8
    if args.input.name != '<stdin>':
        args.input = codecs.open(args.input.name, encoding='utf-8')
    if args.output.name != '<stdout>':
        args.output = codecs.open(args.output.name, 'w', encoding='utf-8')

    unprocess_prpe(args.input,args.output,args.marker1,args.marker2,args.mode)
