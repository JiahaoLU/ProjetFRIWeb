from typing import Tuple, List, Iterator, Generator


class GNode(object):
    def __init__(self, key):
        self.key = key
        self._children = []
        self.parent = None

    def __str__(self):
        return self.key.__str__()

    def __repr__(self):
        return self.key.__str__()

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, baby):
        if baby is None:
            self._children.append(baby)
        else:
            if baby not in self._children:
                self._children.append(baby)
            baby.parent = self

    def display(self, _prefix="", _last=True):
        print(_prefix, "\\- " if _last else "|- ", self, sep="")
        _prefix += "     " if _last else "|    "
        child_count = len(self.children)
        for i, child in enumerate(self.children):
            _last = i == (child_count - 1)
            child.display(_prefix, _last)

    def parentheses_presentation(self):
        if not self.children:
            print('()', end='')
        else:
            print('(', end='')
            for child in self.children:
                if child is not None:
                    child.parentheses_presentation()
            print(')', end='')


class TNode(GNode):
    def __init__(self, pair: Tuple[int, int]):
        super().__init__(pair)
        self.id = pair[0]  # (id, tf)
        self.priority = pair[1]
        self.left = None
        self.right = None

    def __repr__(self):
        return "{0}-{1}-{2}-{3}".format(self.id, self.priority,
                                        (self.left.id if self.left is not None else 'N'),
                                        (self.right.id if self.right is not None else 'N'))

    def display(self):
        lines, _, _, _ = self._display_aux()
        for line in lines:
            print(line)

    def _display_aux(self):
        """Returns list of strings, width, height, and horizontal coordinate of the root."""
        s = self.__str__()
        u = len(s)
        # No child.
        if self.right is None and self.left is None:
            height = 1
            middle = u // 2
            return [s], u, height, middle

        # Only left child.
        if self.right is None:
            lines, n, p, x = self.left._display_aux()
            first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s
            second_line = x * ' ' + '/' + (n - x - 1 + u) * ' '
            shifted_lines = [line + u * ' ' for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, n + u // 2

        # Only right child.
        if self.left is None:
            lines, n, p, x = self.right._display_aux()
            first_line = s + x * '_' + (n - x) * ' '
            second_line = (u + x) * ' ' + '\\' + (n - x - 1) * ' '
            shifted_lines = [u * ' ' + line for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, u // 2

        # Two children.
        left, n, p, x = self.left._display_aux()
        right, m, q, y = self.right._display_aux()
        first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s + y * '_' + (m - y) * ' '
        second_line = x * ' ' + '/' + (n - x - 1 + u + y) * ' ' + '\\' + (m - y - 1) * ' '
        if p < q:
            left += [n * ' '] * (q - p)
        elif q < p:
            right += [m * ' '] * (p - q)
        zipped_lines = zip(left, right)
        lines = [first_line, second_line] + [a + u * ' ' + b for a, b in zipped_lines]
        return lines, n + m + u, max(p, q) + 2, n + u // 2


class Treap(object):
    def __init__(self):
        self.root = None
        self.height = 0

    def insert(self, init_value: Tuple[int, int]):
        new_node = TNode(init_value)
        if self.root is None:
            self.root = new_node
        else:
            lefts, rights = self.split(self.root, init_value[0] - 1)
            self.root = self.merge(lefts, new_node)
            self.root = self.merge(self.root, rights)
        self.height = self.get_height(self.root)

    def split(self, joint: TNode, key: int) -> Tuple[TNode, TNode]:
        if joint is None:
            return None, None
        if joint.id > key:
            left, joint.left = self.split(joint.left, key)
            return left, joint
        else:
            joint.right, right = self.split(joint.right, key)
            return joint, right

    def merge(self, left: TNode, right: TNode) -> TNode:
        if left is None:
            return right
        elif right is None:
            return left
        elif left.priority >= right.priority:
            left.right = self.merge(left.right, right)
            return left
        else:
            right.left = self.merge(left, right.left)
            return right

    def get_height(self, node: TNode) -> int:
        if node is None:
            return 0
        return max(1, self.get_height(node.left) + 1, self.get_height(node.right) + 1)

    def search_min_id(self) -> int:
        node = self.root
        while node.left is not None:
            node = node.left
        return node.id


class Gtree:
    def __init__(self, root: GNode = None):
        self.root = root

    def fake_root_for_treap(self, treap_root: TNode):
        self.root = GNode('vr')
        tr = GNode((treap_root.id, treap_root.priority))
        self.root.children = tr
        return tr

    def compress_treap(self, tnode: TNode, gnode: GNode):
        if tnode.left is None and tnode.right is None:
            return
        if tnode.left is not None:
            left_child = GNode((tnode.id - tnode.left.id, tnode.priority - tnode.left.priority))
            gnode.children = left_child
            self.compress_treap(tnode.left, left_child)
        if tnode.right is not None:
            right_sibling = GNode((tnode.right.id - tnode.id, tnode.priority - tnode.right.priority))
            gnode.parent.children = right_sibling
            self.compress_treap(tnode.right, right_sibling)






if __name__ == "__main__":
    Q = ["realistc", "marxism", "conflict"]
    fake_posting_lists = {
        ('realistic', 5): {(71, 4), (163, 1), (326, 1), (332, 1), (365, 3)},
        ('conflict', 15): {(71, 1), (204, 1), (268, 5), (297, 1), (320, 1),
                           (365, 1), (380, 1), (381, 1), (404, 2), (418, 1),
                           (445, 1), (449, 2), (459, 1), (522, 1),
                           (557, 1)},
        ('marxism', 4): {(163, 1), (365, 1), (459, 2), (509, 1)},
        ('reverse', 0): {(30, 24), (13, 14), (35, 6), (4, 6), (22, 2), (44, 3),
                         (9, 2), (15, 1), (27, 1), (39, 2), (14, 1), (37, 1)}
    }
    TREAP = Treap()
    for pair in fake_posting_lists[('reverse', 0)]:
        TREAP.insert(pair)
    print("treap height = ", TREAP.height)
    TREAP.root.display()
    print("min id = ", TREAP.search_min_id())

    GENERAL_TREE = Gtree()
    GENERAL_TREE.compress_treap(TREAP.root, GENERAL_TREE.fake_root_for_treap(TREAP.root))
    GENERAL_TREE.root.display()

    print('Parentheses presentation: ', end='')
    GENERAL_TREE.root.parentheses_presentation()

