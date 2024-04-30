import bisect
import math

# 展平嵌套列表
def flatten(l):
    return [y for x in l for y in x]


class Leaf:
    def __init__(self, previous_leaf, next_leaf, parent, b_factor):
        self.previous = previous_leaf # 前一个叶子节点
        self.next = next_leaf # 后一个叶子节点
        self.parent = parent # 父节点
        self.b_factor = b_factor # B+树的阶数
        self.a_factor = math.ceil(b_factor/2) # 阶数的一半
        self.keys = [] # 关键字
        self.children = [] # 值
    
    @property
    def is_root(self):
        return self.parent is None 

    def insert(self, key, value):
        index = bisect.bisect_left(self.keys, key) # 返回key应该插入的位置
        if index < len(self.keys) and self.keys[index] == key: # 如果key已经存在
            self.children[index].append(value) 
        else: # 如果key不存在
            self.keys.insert(index, key) 
            self.children.insert(index, [value])
            if(index== len(self.keys)-1):
                self.update2b_help(self)
            if len(self.keys) > self.b_factor:
                split_index = math.ceil(self.b_factor/2)
                self.split(split_index) # 分裂

    def get(self, key):
        index = bisect.bisect_left(self.keys, key)
        if index < len(self.keys) and self.keys[index] == key:
            return self.children[index]
        else:
            return None

    def split(self, index):
        new_leaf_node = Leaf(self, self.next, self.parent, self.b_factor)# 新建一个叶子节点 其实是链表插入
        new_leaf_node.keys = self.keys[index:]
        new_leaf_node.children = self.children[index:]
        self.keys = self.keys[:index]
        self.children = self.children[:index]
        if self.next is not None:
            self.next.previous = new_leaf_node
        self.next = new_leaf_node
        if self.is_root: #一对一的关系
            self.parent = Node(None, None, [self.keys[-1],new_leaf_node.keys[-1]], [self, self.next], b_factor=self.b_factor, parent=None)
            self.next.parent = self.parent
        else:
            self.parent.add_child(self.keys[-1], self.next)

    def find_left(self, key, include_key=True):
        items = []
        index = bisect.bisect_right(self.keys, key) - 1 # 存在则返回索引 
        if index == -1:
            items = []
        else:
            if include_key:
                items = self.children[:index+1]
            else:
                if key == self.keys[index]:
                    index -= 1
                items = self.children[:index+1]
        return self.left_items() + flatten(items) # 展平

    def find_right(self, key, include_key=True):
        items = []
        index = bisect.bisect_left(self.keys, key) # 返回索引
        if index == len(self.keys):
            items = []
        else:
            if include_key:
                items = self.children[index:]
            else:
                if key == self.keys[index]:
                    index += 1
                items = self.children[index:]
        return flatten(items) + self.right_items()

    def left_items(self):
        items = []
        node = self
        while node.previous is not None:
            node = node.previous
        while node != self:
            for elem in node.children:
                if type(elem) == list:
                    items.extend(elem)
                else:
                    items.append(elem)
            node = node.next
        return items

    def right_items(self):
        items = []
        node = self.next
        while node is not None:
            for elem in node.children:
                if type(elem) == list:
                    items.extend(elem)
                else:
                    items.append(elem)
            node = node.next
        return items
    
    # 处理更新的值小于原值 
    def update2s_help(self,change_node):
        node = change_node.parent
        while node is not None:
            update_index = bisect.bisect_left(node.keys,change_node.keys[-1])
            node.keys[update_index] = node.children[update_index].keys[-1]
            node=node.parent
    # 处理更新的值大于原值 右借、左合
    def update2b_help(self,change_node):
        node = change_node.parent
        while node is not None:
            update_index = bisect.bisect_left(node.keys,change_node.keys[-1])-1
            node.keys[update_index] = node.children[update_index].keys[-1]
            node=node.parent

    def delete(self, key):
        index = bisect.bisect_left(self.keys, key)
        parent_index = bisect.bisect_left(self.parent.keys, key)
        if len(self.keys) > self.a_factor: # 未发生下溢
            if index + 1 == len(self.keys):
                self.keys.pop(index)
                self.children.pop(index)
                self.parent.keys[parent_index] = self.keys[-1]
            else:
                self.keys.pop(index)
                self.children.pop(index)
        elif self.previous is not None and len(self.previous.keys) > self.a_factor: # 从左兄弟节点借
            if index + 1 == len(self.keys):# 删的是末尾
                self.keys.pop(index)
                self.children.pop(index)
                self.keys.insert(0, self.previous.keys.pop())
                self.children.insert(0, self.previous.children.pop())
                # 左兄弟和本节点的parent变化
                self.update2s_help(self.previous)
                self.update2s_help(self)
            else:
                self.keys.pop(index)
                self.children.pop(index)
                self.keys.insert(0, self.previous.keys.pop())
                self.children.insert(0, self.previous.children.pop())
                self.update2s_help(self.previous)
        elif self.next is not None and len(self.next.keys) > self.a_factor: # 从右兄弟节点借
            self.keys.pop(index)
            self.children.pop(index)
            self.keys.append(self.next.keys.pop(0))
            self.children.append(self.next.children.pop(0))
            self.update2b_help(self)
        elif self.previous is not None: # 合并至左兄弟节点
            self.keys.pop(index)
            self.children.pop(index)
            self.previous.keys.extend(self.keys)
            self.previous.children.extend(self.children)
            self.previous.next = self.next
            if self.next is not None:
                self.next.previous = self.previous
            self.parent.keys.pop(parent_index)
            self.parent.children.pop(parent_index)
            self.update2b_help(self.previous)
        elif self.next is not None: # 合并至右兄弟节点
            self.keys.pop(index)
            self.children.pop(index)
            self.next.keys = self.keys + self.next.keys
            self.next.children = self.children + self.next.children
            self.next.previous = self.previous
            if self.previous is not None:
                self.previous.next = self.next
            self.parent.keys.pop(parent_index)
            self.parent.children.pop(parent_index)
        else:
            print("Error: No sibling node to merge")  
            
            # 修补父节点
            node=self.parent
            while node is not None:
                node.fix_underflow()
                node=node.parent


    def items(self):
        return zip(self.keys, self.children)

class Node:
    def __init__(self, previous_node, next_node, keys, children, b_factor, parent=None):
        self.previous = previous_node
        self.next = next_node
        self.keys = keys
        self.children = children
        self.b_factor = b_factor
        self.a_factor = math.ceil(b_factor / 2)
        self.parent = parent

    @property
    def degree(self):
        return len(self.children)

    @property
    def is_root(self):
        return self.parent is None

    def insert(self, key, value):
        index = bisect.bisect_right(self.keys, key)
        if(index == len(self.keys)):
            index -= 1
        node = self.children[index]
        node.insert(key, value)

    def get(self, key):
        index = bisect.bisect_left(self.keys, key)
        return self.children[index].get(key)

    def find_left(self, key, include_key=True):
        index = bisect.bisect_left(self.keys, key)
        return self.children[index].find_left(key, include_key)

    def find_right(self, key, include_key=True):
        index = bisect.bisect_left(self.keys, key)
        return self.children[index].find_right(key, include_key)

    def add_child(self, key, child):
        index = bisect.bisect_right(self.keys, key)
        self.keys.insert(index, key)
        self.children.insert(index+1, child) # +1是因为后插入的节点是在右边
        if self.degree > self.b_factor:
            split_index = math.floor(self.b_factor / 2)
            self.split(split_index)

    def split(self, index):
        split_key = self.keys[index]
        # 新节点index+1 前节点:index+1
        new_node = Node(self, self.next, self.keys[index+1:], self.children[index+1:], self.b_factor, self.parent)
        for node in self.children[index+1:]:
            node.parent = new_node
        self.keys = self.keys[:index+1]
        self.children = self.children[:index+1] # why +1

        if self.next is not None:
            self.next.previous = new_node
        self.next = new_node
        if self.is_root:
            self.parent = Node(None, None, [split_key,new_node.keys[-1]], [self, self.next], b_factor=self.b_factor, parent=None)
            self.next.parent = self.parent
        else:
            self.parent.add_child(split_key, self.next)

    # 处理更新的值小于原值 
    def update2s_help(self,change_node):
        node = change_node.parent
        while node is not None:
            update_index = bisect.bisect_left(node.keys,change_node.keys[-1])
            node.keys[update_index] = node.children[update_index].keys[-1]
            node=node.parent
    # 处理更新的值大于原值 右借、左合
    def update2b_help(self,change_node):
        node = change_node.parent
        while node is not None:
            update_index = bisect.bisect_left(node.keys,change_node.keys[-1])-1
            node.keys[update_index] = node.children[update_index].keys[-1]
            node=node.parent
            
    def fix_underflow_help(self):
        parent_index = bisect.bisect_left(self.parent.keys, self.keys[-1])
        if len(self.keys) < self.a_factor:
            if self.previous is not None and len(self.previous.keys) > self.a_factor:
                # 从左兄弟节点借
                self.keys.insert(0, self.previous.keys.pop())
                self.children.insert(0, self.previous.children.pop())
                self.update2s_help(self.previous)
            elif self.next is not None and len(self.next.keys) > self.a_factor:
                # 从右兄弟节点借
                self.keys.append(self.next.keys.pop(0))
                self.children.append(self.next.children.pop(0))
                self.update2b_help(self)
            elif self.previous is not None:
                # 合并至左兄弟节点
                self.previous.keys.extend(self.keys)
                self.previous.children.extend(self.children)
                self.previous.next = self.next
                if self.next is not None:
                    self.next.previous = self.previous
                parent_index = bisect.bisect_left(self.parent.keys, self.keys[-1])
                self.parent.keys.pop(parent_index)
                self.parent.children.pop(parent_index)
                self.update2b_help(self.previous)
            elif self.next is not None:
                # 合并至右兄弟节点
                self.next.keys = self.keys + self.next.keys
                self.next.children = self.children + self.next.children
                self.next.previous = self.previous
                if self.previous is not None:
                    self.previous.next = self.next
                for i in range(len(self.children)):
                    self.children[0].parent = self.next
                parent_index = bisect.bisect_left(self.parent.keys, self.keys[-1])
                self.parent.keys.pop(parent_index)
                self.parent.children.pop(parent_index)
            else:
                print("fix failed")

    def fix_underflow(self):
        flag=[0,0,0]
        # delete后可能会引起下溢内部节点
        potential_node = [self.previous,self,self.next]
        for i in range(3):
            if potential_node[i] is not None:
                if len(potential_node[i].keys) < self.a_factor:
                    flag[i]=1                    
        for i in range(3):
            if flag[i]==1 and potential_node[i].is_root==False:
                potential_node[i].fix_underflow_help()

    def delete(self, key):
        index = bisect.bisect_left(self.keys, key)
        self.children[index].delete(key)