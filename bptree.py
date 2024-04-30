from node import Leaf, Node

class BPlusTree:
    def __init__(self, b_factor=32):
        self.b_factor = b_factor
        self.root = Leaf(None, None, None, b_factor)
        self.size = 0

    #可以通过[]来访问
    def __getitem__(self, key):
        return self.get(key)

    # 可以通过len(bplustree)来访问
    def __len__(self):
        return self.size

    @property
    def keys(self):
        leaf = self.leftmost_leaf()
        ks = []
        while leaf is not None:
            ks.extend(leaf.keys)
            leaf = leaf.next
        return ks
    
    @property
    def values(self):
        leaf = self.leftmost_leaf()
        vals = []
        while leaf is not None:
            for elem in leaf.children:
                if type(elem) == list:
                    vals.extend(elem)
                else:
                    vals.append(elem)
            leaf = leaf.next
        return vals

    @property
    def height(self):
        node = self.root
        height = 0
        while type(node) != Leaf:
            height += 1
            node = node.children[0]
        return height
    
    def insert(self, key, value):
        self.root.insert(key, value) # 插入
        self.size += 1
        # 如果根节点不再是叶子节点
        if self.root.parent is not None:
            self.root = self.root.parent

    def get(self, key):
        return self.root.get(key)
    
    def range_search(self, notation, cmp_key):
        notation = notation.strip()
        if notation not in [">", "<", ">=", "<="]:
            raise Exception("Nonsupport notation: {}. Only '>' '<' '>=' '<=' are supported".format(notation))
        if notation == '>':
            return self.root.find_right(cmp_key, False)
        if notation == '>=':
            return self.root.find_right(cmp_key, True)
        if notation == '<':
            return self.root.find_left(cmp_key, False)
        if notation == '<=':
            return self.root.find_left(cmp_key, True)

    def search(self, notation, cmp_key):
        notation = notation.strip()
        if notation not in [">", "<", ">=", "<=", "==", "!="]:
            raise Exception("Nonsupport notation: {}. Only '>' '<' '>=' '<=' '==' '!=' are supported".format(notation))
        if notation == '==':
            res = self.get(cmp_key)
            if res is None:
                return []
            else:
                return res
        if notation == '!=':
            return self.root.find_left(cmp_key, False) + self.root.find_right(cmp_key, False)
        return self.range_search(notation, cmp_key)

    def show(self):
        layer = 0
        node = self.root
        while node is not None:
            print("Layer: {}".format(layer))
            inner_node = node
            while inner_node is not None:
                print(inner_node.keys, end=' ')
                inner_node = inner_node.next
            print('')
            node = node.children[0]
            layer += 1
            if type(node) != Leaf and type(node) != Node:
                break

    def leftmost_leaf(self):
        leaf = self.root
        while type(leaf) != Leaf:
            leaf = leaf.children[0]
        return leaf

    def items(self):
        leaf = self.leftmost_leaf()
        items = []
        while leaf is not None:
            pairs = list(leaf.items())
            items.extend(pairs)
            leaf = leaf.next
        return items

    def delete(self,key):
        if len(self.search('==',key))==0:
            print("key not found")
            return None
        else:
            self.root.delete(key)
            if len(self.root.keys) == 1:
                self.root = self.root.children[0]
                self.root.parent = None
            self.size -= 1


if __name__ == '__main__':
    #测试树功能是否完善
    nums=[10,15,37,44,51,59,63,85]
    t = BPlusTree(3)
    for num in nums:
        t.insert(num,num)
    t.show()
    t.delete(37)
    t.show()
    t.insert(38,38)
    t.show()