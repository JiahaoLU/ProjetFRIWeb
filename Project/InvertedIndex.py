# encoding: utf-8
"""
@author: Jiahao LU
@contact: lujiahao8146@gmail.com
@file: Main.py
@time: 2020/3/19
@desc: Functions and classes for generating inverted index
"""
from typing import TypeVar, Iterable, List, Set, Dict, Tuple
from math import log10
from copy import deepcopy
import os
from nltk.stem import WordNetLemmatizer
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
import pickle as pkl
from tqdm import tqdm


def plot_bar(xx: Iterable, yy: Iterable, title):
    """
    plotting util function
    :param xx: variable x
    :param yy: varable y
    :param title: title of the graph
    :return:
    """
    plt.style.use('dark_background')
    plt.figure(figsize=(6, 10))
    plt.rc('ytick', labelsize=8)
    sns.barplot(x=yy, y=xx)
    plt.title(title)
    plt.show()


def clean_lemmatize_count(words: Iterable[str], counter: Counter = None, do_rm_stpw=False) -> Iterable[str]:
    """
    ALL TERMS WILL BE STORED IN MINUSCULE
    Cleaning: lower the words; skip & remove meaningless punctuations
    Lemmatisation: Get singular form, original form of a verb
    Count: count the occurrence of tokens to facilitate the deletion of stop words
    :param words: List of words
    :param counter: Counter of all tokens in the collection
    :param do_rm_stpw: bool for if stop words will be removed
    :return: List of treated tokens
    """
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
    """
    Remove stop words from word bag
    :param bag: Word bag where the key is document id and the value is the list of tokens the document contains.
    :param counter: Count the occurrence of tokens and help show the most common tokens as candidate of stp words
    :param threshold: Maximal number of stop words which will be removed
    :param method: 'direct' : Remove directly number of threshold of stop words from the most common tokens
                    'from-known' : Compare with the already known stop word list and remove the most common ones so that
                                    those meaningful high-frequent tokens will not be removed
    :return: The function modifies the word bag and return nothing only when there is an error.
    """
    if threshold <= 0:
        print('Threshold must be larger than 0.')
        return
    if method == 'direct':
        stop_words = [t[0] for t in counter.most_common(threshold)]
    elif method == 'from-known':
        try:
            with open('./Stop_words.txt', 'r') as stpwf:
                known_stop_words = set()
                for line in stpwf.readlines():
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
    plot_bar(stop_words, [counter[stp] for stp in stop_words], 'Most Common Tokens in the Corpus')
    condition = lambda t: t not in stop_words
    for key, tokens in bag.items():
        bag[key] = list(filter(condition, tokens))


def get_terms_in_bag(collection_folder: str, do_rm_stpw=True, stop_word_threshold: int = 100) -> Tuple[str, Dict, Dict]:
    """
    The function read collection files and map document url name into id;
    and get token list of each document into a dictionary with document id as the key;
    Stop words can be chosen to be removed
    :param collection_folder: The top-level collection folder
    :param do_rm_stpw: bool for if stop words will be removed
    :param stop_word_threshold: Maximal number of stop words which will be removed
    :return: repo: name of sub-collection for sake of file storage
             docid: mapping from doc_id to sub-collection name and document url name
             bag: dictionary of tokens contained in each document
    """
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
            id_gen = 0
            counter = Counter()
            for root, _, files in os.walk(os.path.join(collection_dir, repo), topdown=True):
                print('Converting files in repository %s' % repo)
                for file in tqdm(iterable=files, total=len(files)):
                    id_gen += 1
                    docid[id_gen] = repo + '/' + file
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as docf:
                        for line in docf:
                            line = clean_lemmatize_count(line.split(' '), counter, do_rm_stpw=do_rm_stpw)
                            if id_gen not in bag.keys():
                                bag[id_gen] = line
                            else:
                                bag[id_gen] += line
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
    """
    The class for constructing posting list for a term
    Example: 'CertainTerm': {
                                df,
                                indexation = {(doc1, tf, list_of_positions), ...}
                             }
    """
    T = TypeVar('T')

    def __init__(self, df: int = 0):
        self.df = df
        self._indexation = set()

    def __repr__(self):
        """
        To better print or write the instances of class
        :return:
        """
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
        """
        Override setter of indexation using concatenation methods
        :param doc: can be list, set, tuple etc...
                    list / set : a bunch of document posting lists
                    tuple: a single document posting
        :return:
        """
        if doc is not None:
            if type(doc) in {list, set}:
                self._indexation.update(doc)
            else:
                self._indexation.add(doc)


class InvertedIndex(dict):
    """
    Class for generating inverted index
    Inherit dict class: key is a term while value is a PostingList object
    """
    def __init__(self):
        """
        doc_id: mapping from document id to document url name
        D: total document amount
        iitype: type of inverted index chosen in {'doc', 'freq', 'pos'}
        """
        super().__init__()
        self.doc_id = None
        # self.doc_bag = None
        self.D = 0
        self.iitype = 'null'

    def __str__(self):
        """
        To better print or write the instances of class
        :return:
        """
        return '\nIndexation type = %s, Document amount = %d, Vocabulary amount = %d,\nInverted index = %s'\
               % (self.iitype, self.D, len(self), super.__str__(self))

    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            print('Keyword \'%s\' not found in document.' % item)
            return PostingList()

    def get_inverted_index(self, doc_id: Dict, doc_bag: Dict, itype='freq'):
        """
        generate inverted index from a bag of tokens
        :param doc_id:
        :param doc_bag:
        :param itype:
        :return:
        """
        self.doc_id = doc_id
        self.D = len(doc_id)
        self._build_inverted_index(doc_bag, itype=itype)

    def _build_inverted_index(self, doc_bag: Dict[int, List[str]], itype='freq'):
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
        """
        From document id get document url name and its sub-collection
        :param doc_key:
        :return:
        """
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
        """
        calculate idf
        :param term:
        :return:
        """
        try:
            return log10(self.D / self.__getitem__(term).df)
        except KeyError:
            print('Keyword not found.')


if __name__ == '__main__':
    from Restitution_of_article.Treap import Treap, Gtree
    from copy import deepcopy
    inver_index_path = 'Inverted_index_treap'
    if not os.path.exists(inver_index_path):
        os.mkdir(inver_index_path)
    stpw_mark = 'nostp'
    with open('./Inverted_index_cs276/collection.cs276.nostp.freq.0.ii', 'rb') as f:
        _ii = pkl.load(f)
        tdict = {}
        for term, posting in _ii.items():
            TREAP = Treap()
            for pair in posting.indexation:
                TREAP.insert(deepcopy(pair))
            print("treap height = ", TREAP.height)

            GENERAL_TREE = Gtree()
            GENERAL_TREE.compress_treap(TREAP.root, GENERAL_TREE.fake_root_for_treap(TREAP.root))
            tdict[term] = (deepcopy(posting.df), GENERAL_TREE.root.parentheses_presentation())
            #

        _repo = 0
        print('Inverted index generated for repository %s' % _repo)
        with open(
                inver_index_path + '/collection.s.' + stpw_mark + '.' + 'freq' + '.' + str(_repo) + '.ii',
                'wb') as f:
            pkl.dump(tdict, f)
        print('Inverted index %s saved on %s.' % (_repo, inver_index_path))

    # with open(inver_index_path + '/collection.s.nostp.freq.0.ii', 'rb') as f:
    #     ii = pkl.load(f)
    #     print(ii.idf('student'))
