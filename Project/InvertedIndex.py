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


def plot_bar(xx, yy, title):
    plt.style.use('dark_background')
    plt.figure(figsize=(6, 10))
    plt.rc('ytick', labelsize=10)
    sns.barplot(x=yy, y=xx)
    plt.title(title)
    plt.show()


def clean_lemmatize_count(words: Iterable[str], counter: Counter, do_rm_stpw=True) -> Iterable[str]:
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


def get_terms_in_bag(collection_folder: str, do_rm_stpw=True, stop_word_threshold: int = 100) -> Tuple[Dict, Dict]:
    # read file
    work_dir = os.getcwd()
    collection_dir = work_dir + '\\' + collection_folder + '\\'
    if os.path.exists(collection_dir):
        sub_repo = [repo for repo in os.listdir(collection_dir) if not os.path.isfile(os.path.join(collection_dir, repo))]
        # walk through files to get words
        bag = dict()
        docid = dict()
        id = 0
        counter = Counter()
        for repo in sub_repo:
            for root, _, files in os.walk(os.path.join(collection_dir, repo), topdown=True):
                for file in files:
                    id += 1
                    docid[id] = repo + '/' + file
                    with open(os.path.join(root, file),'r', encoding='utf-8') as f:
                        for line in f:
                            line = clean_lemmatize_count(line.split(' '), counter, do_rm_stpw=do_rm_stpw)
                            bag[id] = line
        if do_rm_stpw:
            remove_stop_words(bag, counter, threshold=stop_word_threshold, method='from-known')
        return docid, bag
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
            self._indexation.add(doc)


class InvertedIndex(dict):
    def __init__(self, src_path: str):
        super().__init__()
        self.doc_id, self.doc_bag = get_terms_in_bag(src_path)
        self.D = len(self.doc_bag)
        self.iitype = 'null'

    def __str__(self):
        return '\nIndexation type = %s, Document amount = %d, Vocabulary amount = %d,\nInverted index = %s'\
               % (self.iitype, self.D, len(self), super.__str__(self))

    def build_inverted_index(self, itype='freq'):
        """

        :param itype: 1-doc index
                     2-frequence index
                     3-position index
        :return:
        """
        if itype not in {'doc', 'freq', 'pos'}:
            raise ValueError('Indexation type not correct (doc/freq/pos).')
        self.iitype = itype
        for doc, terms in self.doc_bag.items():
            cnt = Counter(terms)
            set_terms = set(terms)
            for term in set_terms:
                posting = PostingList()
                if term in self.keys():
                    posting = deepcopy(self[term])
                posting.df += 1
                if itype == 'doc':
                    posting.indexation = doc
                elif itype == 'freq':
                    posting.indexation = (doc, cnt[term])
                else:
                    posting.indexation = (doc, cnt[term], ([i for i, t in enumerate(terms) if t == term]))
                    # position of word (to do : of starting character)
                super().__setitem__(term, posting)

    def get_doc_url(self, doc_id: int) -> str:
        return self.doc_id[doc_id]

    def idf(self, term: str) -> float:
        if term in self.keys():
            return log10(self.D / self[term].df)
        else:
            raise KeyError('Term not in the term bag.')


if __name__ == '__main__':
    ii = InvertedIndex('Collection')
    ii.build_inverted_index()
    save_dir = 'collection.s.ii'
    if os.path.exists(os.path.join(os.getcwd(), save_dir)):
        os.remove(os.path.join(os.getcwd(), save_dir))
    with open(save_dir, 'wb') as f:
        pkl.dump(ii, f)








