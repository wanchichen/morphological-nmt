#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Jānis Zuters

"""Use operations learned with learn_prpe.py to encode a new text.
"""

from __future__ import unicode_literals, division

import sys
import codecs
import argparse

from io import open
argparse.open = open

from prpe import apply_prpe

def create_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="learn PPE-based word segmentation")
    parser.add_argument(
        '--input', '-i', type=argparse.FileType('r'), default=sys.stdin,
        metavar='PATH',
        help="Input file (default: standard input).")
    parser.add_argument(
        '--output', '-o', type=argparse.FileType('w'), default=sys.stdout,
        metavar='PATH',
        help="Output file (default: standard output)")
    parser.add_argument(
        '--prefixes', '-p', type=argparse.FileType('r'),
        metavar='PATH',
        help="Intput file of PRPE prefixes")
    parser.add_argument(
        '--roots', '-r', type=argparse.FileType('r'),
        metavar='PATH',
        help="Intput file of PRPE roots")
    parser.add_argument(
        '--suffixes', '-s', type=argparse.FileType('r'),
        metavar='PATH',
        help="Intput file of PRPE suffixes")
    parser.add_argument(
        '--postfixes', '-t', type=argparse.FileType('r'),
        metavar='Intput',
        help="Output file of PRPE postfixes")
    parser.add_argument(
        '--endings', '-u', type=argparse.FileType('r'),
        metavar='PATH',
        help="Intput file of PRPE raw prefixes")
    parser.add_argument(
        '--words', '-w', type=argparse.FileType('r'),
        metavar='PATH',
        help="Intput file of most frequent words")
    parser.add_argument(
        '--marker1', '-m', type=str, default='9474', metavar='STR',
        help="Segmentation marker (default: '%(default)s'))")
    parser.add_argument(
        '--marker2', '-n', type=str, default='9553', metavar='STR',
        help="Uppercase marker (default: '%(default)s'))")
    parser.add_argument(
        '--mode', '-d', type=int, default=1,
        help="Marking and optimization mode of segmentation")
    parser.add_argument(
        '--genroots', '-g', type=int, default=0,
        help="Try to generate possible roots")
    parser.add_argument(
        '--language', '-l', type=str, default='lv',
        help="Number of prp learning iterations")
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
    args.prefixes = codecs.open(args.prefixes.name, 'r', encoding='utf-8')
    args.roots = codecs.open(args.roots.name, 'r', encoding='utf-8')
    args.suffixes = codecs.open(args.suffixes.name, 'r', encoding='utf-8')
    args.postfixes = codecs.open(args.postfixes.name, 'r', encoding='utf-8')
    args.endings = codecs.open(args.endings.name, 'r', encoding='utf-8')
    args.words = codecs.open(args.words.name, 'r', encoding='utf-8')

    apply_prpe(args.input, args.output, args.prefixes, args.roots, args.suffixes, args.postfixes, args.endings, args.words,
               args.marker1, args.marker2, args.mode, args.genroots, args.language)
