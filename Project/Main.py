# encoding: utf-8
"""
@author: Jiahao LU
@contact: lujiahao8146@gmail.com
@file: Main.py
@time: 2020/3/19
@desc:
"""
from __future__ import print_function
import os
import sys
import argparse
from InvertedIndex import InvertedIndex, PostingList
import pickle as pkl


def run_module(inver_index_path):
    with open(inver_index_path, 'rb') as iif:
        ii = pkl.load(iif)
        print(ii)
    # to do


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-invidx_dir', default=None, type=str, required=True,
                        help="File path (postfix .ii) where inverted index are stored.")
    args = parser.parse_args()

    if os.path.exists(args.invidx_dir) or os.path.exists(os.path.join(os.getcwd(), args.invidx_dir)):
        run_module(args.invidx_dir)
    else:
        raise FileNotFoundError('Inverted index file not found.')


if __name__ == '__main__':
    main()
