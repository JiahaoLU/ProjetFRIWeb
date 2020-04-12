# encoding: utf-8
"""
@author: Jiahao LU
@contact: lujiahao8146@gmail.com
@file: QueryModule.py
@time: 2020/3/20
@desc: Different query modules here
"""
from tt import BooleanExpression
from Project.InvertedIndex import PostingList, InvertedIndex, clean_lemmatize_count
from typing import List, TypeVar, Tuple, Iterable, Dict
from abc import ABC, abstractmethod
from collections import Counter
from math import sqrt
from Restitution_of_article.Treap import Treap
from Restitution_of_article.FastQuery import intersection, union


def clean_query(q: str) -> str:
    """
    Get cleaned, lemmatized and lower cased query string
    :param q:
    :return:
    """
    lemma_words = clean_lemmatize_count(q.split(' '))
    return ' '.join(lemma_words)


class QueryModule(object):
    T = TypeVar('T')

    def __init__(self, query: str):
        self._query = query

    def __str__(self):
        return ''

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, q: str):
        self._query = q

    @abstractmethod
    def get_result(self, context: T, nbest: int):
        pass


class BoolModule(QueryModule):
    def __init__(self, query: str):
        super().__init__(query)

    def __str__(self):
        return 'Using BoolModule. Compatible with boolean queries\nwith and/or/not.'

    def get_result(self, inverted_index: InvertedIndex, nbest: int) -> List[str]:
        bool_operators = {'and', 'or', 'not'}
        try:
            postfix = self._transform_bool_query_to_postfix()
        except:
            postfix = self._transform_query_to_boolean()
        operands = []  # list of posting lists
        while postfix:
            oper = postfix.pop(0)
            if oper.lower() not in bool_operators:
                operands.append(inverted_index[oper.lower()])
            else:
                try:
                    term2 = operands.pop(-1)
                    term1 = operands.pop(-1)
                    new_operand = PostingList()
                    new_operand.indexation = self._merge_postings_list(oper, term1, term2)
                    operands.append(new_operand)
                    if oper.lower() == 'not':
                        operands.append(new_operand)
                except IndexError:
                    default_operand = PostingList()
                    default_operand.indexation = self._merge_postings_list('')
                    operands.append(default_operand)
        for i in operands.pop(-1).indexation:
            # print(inverted_index.get_doc_url(i))

            yield inverted_index.get_doc_url(i)

    def _transform_query_to_boolean(self) -> List:
        """
        Transform natural language into postfix token list
        :return:
        """
        return BooleanExpression(self.query.lower().replace(' ', ' and ')).postfix_tokens

    def _transform_bool_query_to_postfix(self) -> List:
        """
        Transform boolean expression into postfix token list
        :return:
        """
        return BooleanExpression(self.query.lower()).postfix_tokens

    def _merge_postings_list(self, bool_operator: str,
                             posting_term1: PostingList = None, posting_term2: PostingList = None) -> List:
        """
        Get list of document ids in combining two posting lists according to tne boolean operator
        :param bool_operator:
        :param posting_term1:
        :param posting_term2:
        :return:
        """
        docs1 = [pos[0] if type(pos) != int else pos for pos in posting_term1.indexation]\
            if posting_term1 is not None else []
        docs2 = [pos[0] if type(pos) != int else pos for pos in posting_term2.indexation]\
            if posting_term2 is not None else []
        if bool_operator.lower() == 'and':
            return [doc for doc in docs1 if doc in docs2]
        elif bool_operator.lower() == 'or':
            return list(set(docs1 + docs2))
        elif bool_operator.lower() == 'not':
            return [d for d in docs1 if d not in docs2]
        else:
            raise ValueError('Operator not found (and/or/not)')


class VectorialModule(QueryModule):

    def __init__(self, query: str):
        super().__init__(query)

    def __str__(self):
        return 'Using VectorialModule.'

    def get_result(self, ii: InvertedIndex, nbest: int) -> List[str]:
        if ii.iitype not in {'freq', 'pos'}:
            raise ValueError('Inverted index must has frequencies for vectorial module.')
        norm_q = 0  # query norm
        norm_d = dict()  # document norms
        scores = dict()  # document scores
        vector_q = self.get_query_vector()  # query vector
        for term_q, tf_q in vector_q.items():  # loop on each term in query
            if term_q not in ii.keys():
                continue
            w_q = tf_q * ii.idf(term_q)  # query term weight = tf * idf
            norm_q += w_q * w_q  # norm = sqrt(sum(weight^2))
            for doc_pos in ii[term_q].indexation:
                doc, tf_d = doc_pos[0], doc_pos[1]
                w_d = tf_d * ii.idf(term_q)  # document term weight = tf * idf
                self.dict_accumulate(dict=norm_d, key=doc, acc=w_d * w_d)  # update document norm
                self.dict_accumulate(dict=scores, key=doc, acc=w_q * w_d)  # update document weight
        for doc in scores.keys():
            scores[doc] /= (sqrt(norm_q) * sqrt(norm_d[doc]))  # cosine similarity
        for doc, score in self.get_descending_scores(scores, nbest):
            # print("Local doc id = %s, score = %.5f" % (str(doc), score))
            yield ii.get_doc_url(doc)

    def get_query_vector(self) -> Counter:
        """
        Transform the query into vector represented by a counter of term frequencies
        :return:
        """
        return Counter(self.query.split(' '))

    def get_descending_scores(self, scores: dict, threshold: int = 100) -> List[Tuple[int, float]]:
        """
        sort the doc list by scores and intercept the first threshold-th results
        :param scores:
        :param threshold:
        :return:
        """
        pair = sorted(list(scores.items()), key=(lambda x: x[1]), reverse=True)
        return pair[:min(len(pair), threshold)]

    def dict_accumulate(self, key, dict: dict, acc):
        """
        Function for updating dictionary
        :param key:
        :param dict:
        :param acc:
        :return:
        """
        if key not in dict.keys():
            dict[key] = acc
        else:
            dict[key] += acc


class TreapModule(QueryModule):

    def __init__(self, query: str):
        super().__init__(query)
        self.is_u = False
        self.treaps = dict()

    def __str__(self):
        return 'Using TreapModule. Add u + /space/ at the beginning of query if it is a union query.'

    @QueryModule.query.setter
    def query(self, q):
        self._query = q
        self.is_u = self.is_union()
        if self.is_union():
            self.query = self.query[2:]

    def get_result(self, ii: InvertedIndex, nbest: int):
        print('Searching ...')
        if self.is_u:
            # function from Restitution_of_article.FastQuery
            res = union(self.query.split(' '), self.treaps, k=nbest, D=ii.D)
        else:
            # function from Restitution_of_article.FastQuery
            res = intersection(self.query.split(' '), self.treaps, k=nbest, D=ii.D)
        for doc, score in res:
            try:
                # print("Local doc id = %s, score = %.5f" % (str(doc), score))
                yield ii.get_doc_url(doc)
            except [AttributeError, KeyError]:
                continue

    def is_union(self):
        """
        Check if the query is a union one or an intersection one
        :return:
        """
        return self.query[0] == 'u' and self.query[1] == ' '

    def build_treaps(self, ii: InvertedIndex):
        """
        Build treaps for terms in query
        :param q:
        :param ii: already known inverted index
        :return:
        """
        treaps = dict()
        for term in self.query.split(' '):
            tree = Treap()
            try:
                for pair in ii[term].indexation:
                    if type(pair) == int:
                        tree.insert((pair, 1))
                    else:
                        tree.insert((pair[0], pair[1]))
                treaps[term] = (ii[term].df, tree)
            except:
                print('Warning while building treap for keyword \'%s\'.' % term)
                continue
        self.treaps = treaps


if __name__ == '__main__':
    vm = VectorialModule('A B C C')
    print([(k,v) for k, v in vm.get_query_vector().items()])