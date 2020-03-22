# encoding: utf-8
"""
@author: Jiahao LU
@contact: lujiahao8146@gmail.com
@file: Main.py
@time: 2020/3/19
@desc:
"""
from typing import TypeVar, Iterable, List, Set, Dict, Tuple
from math import log10
from copy import deepcopy
import os
import shutil
from nltk.stem import WordNetLemmatizer
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
import pickle as pkl
from tqdm import tqdm


def plot_bar(xx, yy, title):
    plt.style.use('dark_background')
    plt.figure(figsize=(6, 10))
    plt.rc('ytick', labelsize=10)
    sns.barplot(x=yy, y=xx)
    plt.title(title)
    plt.show()


def clean_lemmatize_count(words: Iterable[str], counter: Counter = None, do_rm_stpw=False) -> Iterable[str]:
    #  ALL TERMS WILL BE STORED IN MINUSCULE
    lemmatizer = WordNetLemmatizer()
    lemma_words = []
    for word in words:
        if word in {'', '\n', '\t', ' ', ':', '\\', '//', ',', '.', '\'', '\"', '\r', '&'}:
            continue
        for symbol in {'\n', '\t', '\r'}:
            if symbol in word:
                word = word.replace(symbol, '')
        token = lemmatizer.lemmatize(word.lower())
        if do_rm_stpw:
            counter[token] += 1
        lemma_words.append(token)
    return lemma_words


def remove_stop_words(bag: Dict, counter: Counter, threshold=100, method='from-known'):
    if threshold <= 0:
        print('Threshold must be larger than 0.')
        return
    if method == 'direct':
        stop_words = [t[0] for t in counter.most_common(threshold)]
    elif method == 'from-known':
        try:
            with open('./Stop_words.txt', 'r') as f:
                known_stop_words = set()
                for line in f.readlines():
                    if line != '\n':
                        known_stop_words.add(line.lower().replace('\n', ''))
        except FileNotFoundError:
            print('Stop word file not found.')
        stop_words = list()
        for t in counter.most_common(len(counter)):
            if t[0] in known_stop_words:
                stop_words.append(t[0])
            if len(stop_words) == threshold:
                break
    else:
        print('Select method = from-known / direct.')
        return
    #plot_bar(stop_words, [counter[stp] for stp in stop_words], 'Most Common Tokens in the Corpus')
    condition = lambda t: t not in stop_words
    for key, tokens in bag.items():
        bag[key] = list(filter(condition, tokens))


def get_terms_in_bag(collection_folder: str, do_rm_stpw=True, stop_word_threshold: int = 100) -> Tuple[str, Dict, Dict]:
    # read file
    work_dir = os.getcwd()
    collection_dir = work_dir + '\\' + collection_folder + '\\'
    print('Getting terms into bag...')
    if os.path.exists(collection_dir):
        sub_repo = [repo for repo in os.listdir(collection_dir)
                    if not os.path.isfile(os.path.join(collection_dir, repo))]
        # walk through files to get words
        for repo in sub_repo:
            bag = dict()
            docid = dict()
            id = 0
            counter = Counter()
            for root, _, files in os.walk(os.path.join(collection_dir, repo), topdown=True):
                print('Converting files in repository %s' % repo)
                for file in tqdm(iterable=files, total=len(files)):
                    id += 1
                    docid[id] = repo + '/' + file
                    with open(os.path.join(root, file),'r', encoding='utf-8') as f:
                        for line in f:
                            line = clean_lemmatize_count(line.split(' '), counter, do_rm_stpw=do_rm_stpw)
                            if id not in bag.keys():
                                bag[id] = line
                            else:
                                bag[id] += line
            if do_rm_stpw:
                print('Removing stop words...')
                remove_stop_words(bag, counter, threshold=stop_word_threshold, method='from-known')
            yield repo, docid, bag
    else:
        raise OSError('Collection folder does not exist.')


def extract_vocabulary(bag):
    vocabulary = set()
    for tokens in bag.values():
        vocabulary.update(tokens)
    return vocabulary


class PostingList(object):
    T = TypeVar('T')

    def __init__(self, df: int = 0):
        self.df = df
        self._indexation = set()

    def __repr__(self):
        tostr = '{ df = ' + str(self.df) + ',\n'
        for i, ii in enumerate(self._indexation):
            if i % 10 == 0:
                tostr += ' ' * 8
            tostr += ii.__str__() + ', '
            if (i + 1) % 10 == 0:
                tostr += '\n'
        tostr += ' }\n'
        return tostr

    @property
    def indexation(self):
        return self._indexation

    @indexation.setter
    def indexation(self, doc: T):
        if doc is not None:
            if type(doc) in {list, set}:
                self._indexation.update(doc)
            else:
                self._indexation.add(doc)


class InvertedIndex(dict):
    def __init__(self):
        super().__init__()
        self.doc_id = None
        # self.doc_bag = None
        self.D = 0
        self.iitype = 'null'

    def __str__(self):
        return '\nIndexation type = %s, Document amount = %d, Vocabulary amount = %d,\nInverted index = %s'\
               % (self.iitype, self.D, len(self), super.__str__(self))

    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            print('Keyword \'%s\' not found in document.' % item)
            return PostingList()

    def get_inverted_index(self, doc_id, doc_bag, itype='freq'):
        self.doc_id = doc_id
        self.D = len(doc_id)
        self._build_inverted_index(doc_bag, itype=itype)

    def _build_inverted_index(self, doc_bag, itype='freq'):
        """

        :param itype: 1-doc index
                     2-frequence index
                     3-position index
        :return:
        """
        if itype not in {'doc', 'freq', 'pos'}:
            raise ValueError('Indexation type not correct (doc/freq/pos).')
        self.iitype = itype
        print('Indexing documents...')
        for doc, terms in tqdm(iterable=doc_bag.items(), total=self.D):
            cnt = Counter(terms)
            set_terms = set(terms)
            for term in set_terms:
                posting = PostingList()
                if term in self.keys():
                    posting = deepcopy(self.__getitem__(term))
                    print(term)
                posting.df += 1
                if itype == 'doc':
                    posting.indexation = doc
                elif itype == 'freq':
                    posting.indexation = (doc, cnt[term])
                else:
                    posting.indexation = (doc, cnt[term], ([i for i, t in enumerate(terms) if t == term]))
                    # position of word (to do : of starting character)
                self.__setitem__(term, posting)
        print('Inverted index done.')

    def get_doc_url(self, doc_key) -> str:
        try:
            if type(doc_key) == int:
                return self.doc_id[doc_key]
            elif type(doc_key) == tuple:
                return self.doc_id[doc_key[0]]
            else:
                return self.doc_id[str(doc_key[0])]
        except (TypeError, ValueError, IndexError):
            print('Posting list not in good type.')
            return ''

    def idf(self, term: str) -> float:
        try:
            return log10(self.D / self.__getitem__(term).df)
        except KeyError:
            print('Keyword not found.')


if __name__ == '__main__':
    inver_index_path = 'Inverted_index_s'
    # if not os.path.exists(inver_index_path):
    #     os.mkdir(inver_index_path)
    # stpw_mark = 'nostp'
    # for id_and_bag in get_terms_in_bag('Collection', do_rm_stpw=False, stop_word_threshold=100):
    #     repo, doc_id, bag = id_and_bag
    #     ii = InvertedIndex()
    #     ii.get_inverted_index(doc_id, bag, itype='freq')
    #
    #     print('Inverted index generated for repository %s' % repo)
    #
    #     with open(
    #             inver_index_path + '/collection.s.' + stpw_mark + '.' + 'freq' + '.' + repo + '.ii',
    #             'wb') as f:
    #         pkl.dump(ii, f)
    #     print('Inverted index %s saved on %s.' % (repo, inver_index_path))

    with open(inver_index_path + '/collection.s.nostp.freq.0.ii', 'rb') as f:
        ii = pkl.load(f)
        print(ii.idf('student'))







