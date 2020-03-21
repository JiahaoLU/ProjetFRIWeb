# encoding: utf-8
"""
@author: Jiahao LU
@contact: lujiahao8146@gmail.com
@file: QueryModule.py
@time: 2020/3/20
@desc:
"""
from tt import BooleanExpression
from InvertedIndex import PostingList, InvertedIndex, clean_lemmatize_count
from typing import List, TypeVar, Tuple
from abc import ABC, abstractmethod
from collections import Counter
from math import sqrt


def clean_query(q: str):
    lemma_words = clean_lemmatize_count(q.split(' '))
    return ' '.join(lemma_words)


class QueryModule(object):
    T = TypeVar('T')

    def __init__(self, query: str):
        self.query = query

    @abstractmethod
    def get_result(self, context: T):
        pass


class BoolModule(QueryModule):
    def __init__(self, query: str):
        super().__init__(query)

    def get_result(self, inverted_index: InvertedIndex) -> List[str]:
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
            print(inverted_index.get_doc_url(i))
            yield inverted_index.get_doc_url(i)

    def _transform_query_to_boolean(self) -> List:
        return BooleanExpression(self.query.lower().replace(' ', ' and ')).postfix_tokens

    def _transform_bool_query_to_postfix(self) -> List:
        return BooleanExpression(self.query.lower()).postfix_tokens

    def _merge_postings_list(self, bool_operator: str,
                             posting_term1: PostingList = None, posting_term2: PostingList = None) -> List:
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

    def get_result(self, ii: InvertedIndex) -> List[str]:
        if ii.iitype not in {'freq', 'pos'}:
            raise ValueError('Inverted index must has frequencies for vectorial module.')
        norm_q = 0
        norm_d = dict()
        scores = dict()
        vector_q = self.get_query_vector()
        for term_q, tf_q in vector_q.items():
            if term_q not in ii.keys():
                continue
            w_q = tf_q * ii.idf(term_q)
            norm_q += w_q * w_q
            for doc_pos in ii[term_q].indexation:
                doc, tf_d = doc_pos[0], doc_pos[1]
                w_d = tf_d * ii.idf(term_q)
                self.dict_accumulate(dict=norm_d, key=doc, acc=w_d * w_d)
                self.dict_accumulate(dict=scores, key=doc, acc=w_q * w_d)
        for doc in scores.keys():
            scores[doc] /= (sqrt(norm_q) * sqrt(norm_d[doc]))
        for doc, score in self.get_descending_scores(scores):
            print("Local doc id = %s, score = %.5f" % (str(doc), score))
            yield ii.get_doc_url(doc)

    def get_query_vector(self) -> Counter:
        return Counter(self.query.split(' '))

    def get_descending_scores(self, scores: dict, threshold: int = 100) -> List[Tuple[int, float]]:
        pair = sorted(list(scores.items()), key=(lambda x: x[1]), reverse=True)
        return pair[:threshold]

    def dict_accumulate(self, key, dict: dict, acc):
        if key not in dict.keys():
            dict[key] = acc
        else:
            dict[key] += acc


if __name__ == '__main__':
    vm = VectorialModule('A B C C')
    print([(k,v) for k, v in vm.get_query_vector().items()])