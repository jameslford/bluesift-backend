from typing import List

class Tree:

    def __init__(self, name, count, children=None):
        self.name = name
        self.count = count
        self.children: List[Tree] = []
        if children:
            self.children = [Tree(**child) for child in children if child]

    def serialize(self):
        return {
            'name': self.name,
            'count': self.count,
            'children': [child.serialize() for child in self.children]
            }
