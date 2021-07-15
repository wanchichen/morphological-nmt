    #!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Jānis Zuters

"""Use prefix-root-postfix encoding (PRPE) to learn a variable-length encoding of the vocabulary in a text.
"""
from __future__ import unicode_literals, division

import sys
import codecs
import argparse

from io import open
argparse.open = open

from prpe import learn_prpe

def create_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="learn PRPE-based word segmentation")
    parser.add_argument(
        '--input', '-i', type=argparse.FileType('r'), default=sys.stdin,
        metavar='PATH',
        help="Input text (default: standard input).")
    parser.add_argument(
        '--prefixes', '-p', type=argparse.FileType('w'),
        metavar='PATH',
        help="Output file for PRPE prefixes")
    parser.add_argument(
        '--roots', '-r', type=argparse.FileType('w'),
        metavar='PATH',
        help="Output file for PRPE roots")
    parser.add_argument(
        '--suffixes', '-s', type=argparse.FileType('w'),
        metavar='PATH',
        help="Output file for PRPE suffixes")
    parser.add_argument(
        '--postfixes', '-t', type=argparse.FileType('w'),
        metavar='PATH',
        help="Output file for PRPE postfixes")
    parser.add_argument(
        '--endings', '-u', type=argparse.FileType('w'),
        metavar='PATH',
        help="Output file for PRPE endings")
    parser.add_argument(
        '--words', '-w', type=argparse.FileType('w'),
        metavar='PATH',
        help="Output file for best words")
    parser.add_argument(
        '--prerate', '-a', type=float, default=25,
        help="How many prefixes to collect (greater than 1 means exact number, less means percentage)")
    parser.add_argument(
        '--sufrate', '-b', type=float, default=400,
        help="How many suffixes to collect (greater than 1 means exact number, less means percentage)")
    parser.add_argument(
        '--postrate', '-c', type=float, default=0.1,
        help="How many postfixes to collect (greater than 1 means exact number, less means percentage)")
    parser.add_argument(
        '--vocabrate', '-v', type=float, default=10000,
        help="How many best words to store to avoid segmentation")
    parser.add_argument(
        '--iterations', type=int, default=1,
        help="Number of prp learning iterations")
    parser.add_argument(
        '--language', '-l', type=str, default='lv',
        help="Number of prp learning iterations")
    parser.add_argument(
        '--goodprefixes', type=argparse.FileType('r'), default=None,
        metavar='PATH',
        help="Input file for good prefixes as exceptions")
    parser.add_argument(
        '--badprefixes', type=argparse.FileType('r'), default=None,
        metavar='PATH',
        help="Input file for bad prefixes as exceptions")
    parser.add_argument(
        '--goodroots', type=argparse.FileType('r'), default=None,
        metavar='PATH',
        help="Input file for good roots as exceptions")
    parser.add_argument(
        '--badroots', type=argparse.FileType('r'), default=None,
        metavar='PATH',
        help="Input file for bad roots as exceptions")
    parser.add_argument(
        '--goodpostfixes', type=argparse.FileType('r'), default=None,
        metavar='PATH',
        help="Input file for good postfixes as exceptions")
    parser.add_argument(
        '--badpostfixes', type=argparse.FileType('r'), default=None,
        metavar='PATH',
        help="Input file for bad postfixes as exceptions")
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
    args.prefixes = codecs.open(args.prefixes.name, 'w', encoding='utf-8')
    args.roots = codecs.open(args.roots.name, 'w', encoding='utf-8')
    args.suffixes = codecs.open(args.suffixes.name, 'w', encoding='utf-8')
    args.postfixes = codecs.open(args.postfixes.name, 'w', encoding='utf-8')
    args.endings = codecs.open(args.endings.name, 'w', encoding='utf-8')
    args.words = codecs.open(args.words.name, 'w', encoding='utf-8')
    if args.goodprefixes is not None:
        args.goodprefixes = codecs.open(args.goodprefixes.name, 'r', encoding='utf-8')
    if args.badprefixes is not None:
        args.badprefixes = codecs.open(args.badprefixes.name, 'r', encoding='utf-8')
    if args.goodroots is not None:
        args.goodroots = codecs.open(args.goodroots.name, 'r', encoding='utf-8')
    if args.badroots is not None:
        args.badroots = codecs.open(args.badroots.name, 'r', encoding='utf-8')
    if args.goodpostfixes is not None:
        args.goodpostfixes = codecs.open(args.goodpostfixes.name, 'r', encoding='utf-8')
    if args.badpostfixes is not None:
        args.badpostfixes = codecs.open(args.badpostfixes.name, 'r', encoding='utf-8')

    learn_prpe(args.input, args.prefixes, args.roots, args.suffixes, args.postfixes, args.endings, args.words,
               args.prerate, args.sufrate, args.postrate, args.vocabrate,
               ingoodpref=args.goodprefixes,inbadpref=args.badprefixes,
               ingoodroot=args.goodroots,inbadroot=args.badroots,
               ingoodpost=args.goodpostfixes,inbadpost=args.badpostfixes,
               iterations=args.iterations,lang=args.language
               )

#def learn_prpe(infile,outfilepref,outfileroot,outfilesuff,outfilepost,outfileend,ratepref=20,ratesuff=400,ratepost=0.1,
#              ingoodpref=None,inbadpref=None,ingoodroot=None,inbadroot=None,ingoodpost=None,inbadpost=None):
 