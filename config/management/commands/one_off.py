from typing import List
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from config.models import SubclassTree
from Products.models import Product

class Tree:

    def __init__(self, cls):
        self.name = cls.__name__
        self.count = cls.objects.count()
        self.children: List[Tree] = []

def tree_serializer(tree: Tree):
    return {
        'name': tree.name,
        'count': tree.count,
        'children': [tree_serializer(child) for child in tree.children]
    }



def looper(current: object, parent: Tree):
    if not current._meta.abstract:
        new_tree = Tree(current)
        parent.children.append(new_tree)
        for sub in current.__subclasses__():
            looper(sub, new_tree)
    else:
        for child in current.__subclasses__():
            looper(child, parent)




class Command(BaseCommand):

    def handle(self, *args, **options):
        tree_product = Tree(Product)
        for sub in Product.__subclasses__():
            looper(sub, tree_product)
        serialized = tree_serializer(tree_product)
        content_type = ContentType.objects.get_for_model(Product)
        stree = SubclassTree.objects.get_or_create(content_type=content_type)[0]
        stree.tree = serialized
        stree.save()






        # def looper(cls: Tree):
        #     if cls._meta.abstract:
        #         for sub in cls.__subclasses__():
        #             looper(sub)
        #     else:

        #     for sub in cls.__subclasses__():
        #         abstract = sub._meta.abstract
        #         if not abstract:
        #             cls.children.append(Tree(sub))
        #         looper(sub)

        # classes = [cls for cls in looper(Product)]
        # print(classes)

        # def looper(cls: Tree):
        #     abstract = cls._meta.abstract
        #     if not abstract:
        #         cls.children = 

        #     for sub in cls:
        #         name = sub.__name__
        #         count = sub.
        #         print(sub._meta.abstract)
