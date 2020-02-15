from typing import List

class Tree:

    def __init__(self, cls):
        self.name = cls._meta.verbose_name_plural.lower().strip()
        self.count = cls.objects.count()
        self.children: List[Tree] = []

    def serialize(self):
        return {
            'name': self.name,
            'count': self.count,
            'children': [child.serialize() for child in self.children]
        }
