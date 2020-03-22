# encoding: utf-8
"""
@author: Jiahao LU
@contact: lujiahao8146@gmail.com
@file: Main.py
@time: 2020/3/19
@desc:
"""
from Restitution_of_article.Treap import TNode, Treap
from typing import Tuple, List, Iterator, Generator, Iterable, Dict
from math import log10
from copy import copy


def build_treaps(posting_lists):
    treaps = dict()
    for key, posting in posting_lists.items():
        tree = Treap()
        for pair in posting:
            tree.insert(pair)
        treaps[key[0]] = (key[1], tree)
    return treaps


def intersection(Q: Iterable[str], treaps: Dict, k: int = 3, D: int = 1000) -> List[Tuple[int, float]]:
    # init
    result = list()
    stacks = dict(zip(Q, [[TNode((D, D))] for _ in range(len(Q))]))
    vt = dict(zip(Q, [treaps[t][1].root for t in Q]))
    U = sum([treaps[t][0] * vt[t].priority for t in Q])
    # print("\n---initialisation---\nU = {0},\nstacks = {1},\nvt = {2}".format(U, stacks, vt))
    d = 1
    L = -100000

    # local functions
    def id_top_stack_t(t: str) -> int:
        if stacks[t]:
            return stacks[t][-1].id
        else:
            return D + 1

    def changev(t: str, v: TNode):
        nonlocal U, vt, D
        U += log10(D / treaps[t][0]) * (v.priority - vt[t].priority)   # idf * tf
        vt[t] = v

    def changed(newd: int):
        nonlocal Q, d
        d = newd
        # print("next document = ", d)
        for t in Q:
            v = vt[t]
            while d >= id_top_stack_t(t):
                v = stacks[t].pop(-1)
            changev(t, v)

    def report(doc: int, s: int):
        nonlocal result, L
        result.append((doc, s))
        result.sort(key=lambda x: x[1])
        if len(result) > k:
            result.pop(0)
            L = result[0][1]

    # main loop
    while d < D:
        if [] in stacks.values():
            break
        while U <= L:
            changed(min([id_top_stack_t(t) for t in Q]))
        ident_d = True
        t = None
        for term, vt_node in vt.items():
            if vt_node.id != d:
                ident_d = False
                t = term  # choose where to advance
                break
        if ident_d:
            report(d, U)
            changed(d + 1)
        else:
            if d < vt[t].id:
                lt = vt[t].left
                if lt is not None:
                    stacks[t].append(vt[t])
                    changev(t, lt)
                else:
                    changed(vt[t].id)
            else:
                rt = vt[t].right
                if rt is not None:
                    changev(t, rt)
                else:
                    changev(t, stacks[t].pop(-1))
                    changed(vt[t].id)
    result.reverse()
    for res in result:
        yield res


def union(Q: Iterable[str], treaps: Dict, k: int = 3, D: int = 1000) -> List[Tuple[int, float]]:
    # init
    next_Q = copy(Q)
    result = list()
    stacks = dict(zip(next_Q, [[TNode((D, D))] for _ in range(len(next_Q))]))
    vt = dict(zip(next_Q, [treaps[t][1].root for t in next_Q]))
    U = 0
    nextdt = dict(zip(next_Q, [treaps[t][1].search_min_id() for t in next_Q]))
    # print("\n---initialisation---\nU = {0},\nstacks = {1},\nvt = {2}".format(U, stacks, vt))
    d = 1
    L = -100000

    # local functions
    def id_top_stack_t(t: str) -> int:
        if stacks[t]:
            return stacks[t][-1].id
        else:
            return D + 1

    def changev(t: str, v: TNode):
        nonlocal U, vt, d, D
        if vt[t].id == d:
            U += log10(D / treaps[t][0]) * vt[t].priority   # idf * tf
        vt[t] = v

    def changed(newd: int):
        nonlocal next_Q, d
        d = newd
        # print("next document = ", d)
        for t in next_Q:
            nextdt[t] = max(nextdt[t], newd)
            v = vt[t]
            while d >= id_top_stack_t(t):
                v = stacks[t].pop(-1)
            changev(t, v)

    def report(doc: int, s: int):
        nonlocal result, L
        result.append((doc, s))
        result.sort(key=lambda x: x[1])
        if len(result) > k:
            result.pop(0)
            L = result[0][1]

    # main loop
    while d < D:
        for t in next_Q:
            if not stacks[t]:
                del stacks[t]
                del vt[t]
                del nextdt[t]
                next_Q.remove(t)
        if not stacks:
            break
        while U <= L:
            changed(min([id_top_stack_t(t) for t in next_Q]))
        ident_d = True
        num_equal = 0
        t = None
        for term, vt_node in vt.items():
            if vt_node.id != d:
                if nextdt[term] == d:
                    t = term  # choose where to advance
                if nextdt[term] <= d:
                    ident_d = False
            else:
                num_equal += 1
        if ident_d:
            if num_equal != 0:
                report(d, U)
                U = 0
                changed(d + 1)
            else:
                changed(min(nextdt.values()))
        else:
            if d < vt[t].id:
                lt = vt[t].left
                if lt is not None:
                    stacks[t].append(vt[t])
                    changev(t, lt)
                else:
                    nextdt[t] = vt[t].id
            else:
                rt = vt[t].right
                if rt is not None:
                    changev(t, rt)
                else:
                    changev(t, stacks[t].pop(-1))
                    nextdt[t] = vt[t].id
    result.reverse()
    for res in result:
        yield res


if __name__ == "__main__":
    Query = ["realistic"]#, "marxism", "conflict"]
    fake_posting_lists = {
        ('realistic', 5): {(71, 4), (163, 1), (326, 1), (332, 1), (381, 1), (365, 3)},
        ('conflict', 15): {(71, 1), (163, 1), (204, 1), (268, 5), (297, 1), (320, 1),
                           (365, 1), (380, 1), (381, 1), (404, 2), (418, 1),
                           (445, 1), (449, 2), (459, 1), (522, 1), (557, 1)},
        ('marxism', 4): {(71, 1), (163, 1), (365, 1), (381, 1), (459, 2), (509, 1)}
    }
    TREAPS = build_treaps(fake_posting_lists)

    for key, df_treap in TREAPS.items():
        print("\n----------treap '{0}', height = {1}-----------\n".format(key, df_treap[1].height))
        df_treap[1].root.display()

    print("-----Intersection query-----")
    print("descending order result: ", "".join(["(%d, %.2f), " % (doc, prio) for doc, prio in intersection(Query, TREAPS, 100)])[:-2])

    print("-----Union query-----")
    print("descending order result: ", "".join(["(%d, %.2f), " % (doc, prio) for doc, prio in union(Query, TREAPS, 100)])[:-2])