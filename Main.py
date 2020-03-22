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
from Project.InvertedIndex import InvertedIndex, PostingList, get_terms_in_bag
from Project.QueryModule import BoolModule, clean_query, VectorialModule, TreapModule
import pickle as pkl
import requests, zipfile, io
from tqdm import tqdm
import time
import sys


class Module:
    def __init__(self):
        self.ii = {}
        self.qm = None

    def f_exists(self, path: str):
        return os.path.exists(path) or os.path.exists(os.path.join(os.getcwd(), path))

    def run_ii_module(self, inver_index_path: str, collection_path: str,
                      gen_idx: bool, itype: str, rm_stpw: bool):
        if gen_idx:
            print('Beginning collection download with URL: http://web.stanford.edu/class/cs276/pa/pa1-data.zip')
            r = requests.get('http://web.stanford.edu/class/cs276/pa/pa1-data.zip', stream=True)
            zip_name = 'collection_cs276.zip'
            block_size = 1024  # 1 Kibibyte
            with tqdm(total=int(r.headers.get('content-length', 0)),
                      unit='iB', unit_scale=True, position=0, leave=False) as pbar:
                with open(zip_name, 'wb') as f:
                    for data in r.iter_content(block_size):
                        pbar.update(len(data))
                        f.write(data)
            print('Unzip file.')
            with zipfile.ZipFile(zip_name, 'r') as zipObj:
                # Extract all the contents of zip file in current directory
                old_name = zipObj.namelist()[0][:-1]
                for file in tqdm(iterable=zipObj.namelist(), total=len(zipObj.namelist())):
                    zipObj.extract(member=file)

            if not self.f_exists(collection_path):
                os.rename(old_name, collection_path)
            else:
                rew = input('Collection folder exists. Rewrite? y/n')
                if rew == 'y':
                    os.remove(collection_path)
                    os.rename(old_name, collection_path)
                else:
                    print('Collection installation interrupted by user.')
                    return
            print('Generating inverted index...')
            if self.f_exists(inver_index_path):
                try:
                    os.remove(inver_index_path)
                except:
                    os.remove(os.path.join(os.getcwd(), inver_index_path))
            os.mkdir(inver_index_path)
            stpw_mark = 'stp' if rm_stpw else 'nostp'
            for id_and_bag in get_terms_in_bag(collection_path, do_rm_stpw= rm_stpw, stop_word_threshold=100):
                repo, doc_id, bag = id_and_bag
                ii = InvertedIndex()
                ii.get_inverted_index(doc_id, bag, itype=itype)
                self.ii[repo] = ii
                print('Inverted index generated for repository %s' % repo)

                with open(
                        inver_index_path + '/collection.cs276.' + stpw_mark + '.' + itype + '.' + repo + '.ii',
                        'wb') as f:
                    pkl.dump(ii, f)
                print('Inverted index %s saved on %s.' % (repo, inver_index_path))
            else:
                print('Inverted index not saved.')

        else:
            if self.f_exists(inver_index_path):
                for root, _, files in os.walk(inver_index_path, topdown=True):
                    for ii in files:
                        print('Getting file %s' % ii)
                        with open(os.path.join(root, ii), 'rb') as iif:
                            self.ii[ii] = pkl.load(iif)
            else:
                raise FileNotFoundError('Inverted index file not found.')

    def run_search_module(self, result_dir: str):
        if self.qm is None:
            raise ValueError('No search module is ready.')
        if not self.f_exists(result_dir) or os.path.isfile(result_dir):
            os.mkdir(result_dir)
        print(self.qm)
        query = input('<<<DocQ research>>>Please enter your keywords: ')
        query_mark = ''.join([c for c in query if c.isalpha()])
        if query != '':
            self.qm.query = clean_query(query)
        else:
            return
        with open(
                result_dir + '/' + query_mark + time.strftime(".%H.%M.%S", time.localtime()) + '.txt',
                'a+') as resf:
            for repo, ii in self.ii.items():
                print('--- result in %s ---' % str(repo))
                for res in self.qm.get_result(ii):
                    resf.write(res + '\n')
        print('Results saved in %s' % result_dir)

    def main(self):
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument('--qm', default=None, type=str, required=True,
                            help='Choose the search module from: bool/vectorial/treap')
        parser.add_argument('--rdir', default=None, type=str, required=True,
                            help='Directory name where query results are saved.')
        parser.add_argument('--iidir', default=None, type=str,
                            help="Folder name (where contains .ii files) where inverted index are stored.")
        parser.add_argument('--cdir', default=None, type=str,
                            help='Directory name where the collection wished to be stored.')
        parser.add_argument('--gi', action='store_true',
                            help='True if generate new inverted index file from downloaded collection.')
        parser.add_argument('--itype', type=str, default='freq',
                            help='Type of inverted index: doc/freq/pos')
        parser.add_argument('--rmsw', action='store_true',
                            help='True if stop words need to be removed.')

        args = parser.parse_args()
        if args.gi and args.cdir is None:
            raise ValueError('Collection directory could not be None if generate new inverted index.')
        if args.qm == 'bool':
            self.qm = BoolModule('')
        elif args.qm == 'vectorial':
            self.qm = VectorialModule('')
        elif args.qm == 'treap':
            self.qm = TreapModule('')
        iidir = 'Project/Inverted_index_cs276' if args.iidir is None else args.iidir
        self.run_ii_module(iidir, args.cdir, args.gi, args.itype, args.rmsw)
        while True:
            self.run_search_module(args.rdir)
            leave = input('Continue? y/n')
            if leave == 'n':
                break


if __name__ == '__main__':
    m = Module()
    m.main()
    sys.exit(0)
    # m.qm = TreapModule('')
    # iidir = 'Project/Inverted_index_cs276'
    # m.run_ii_module(iidir, None, False, itype='freq', rm_stpw=False)
    # while True:
    #     m.run_search_module('results')
    #     leave = input('Continue? y/n')
    #     if leave == 'n':
    #         break
