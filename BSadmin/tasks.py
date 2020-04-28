from typing import List
from django.db.transaction import TransactionManagementError
from django.core.mail import EmailMessage
from django.contrib.contenttypes.models import ContentType
from django.db.utils import IntegrityError
from config.celery import app
from Search.models import SearchIndex
from SpecializedProducts.models import FinishSurface, ProductSubClass
from Products.models import Manufacturer


"""
example for met tag:
for manufacturer in manufacturers:s
    labl = manu.label
    finishes = product.sublclasses.filter(manu=manufacturer).values_list('finishes, flat=True)
"""

# @transaction.atomic
@app.task
def create_indexes():
    all_si = SearchIndex.objects.all()
    all_si.delete()
    SearchIndex.create_refresh_suppliers()
    SearchIndex.create_refresh_products()
    __create_static_indexes()
    # __create_fs_indexes()


def __create_manu_collections_indexes():
    pass


def __create_manu_styles_indexes():
    pass


def __create_facet_indexes():
    pass


def __create_tree_index(cls):
    model_types = [cls] + cls._meta.get_parent_list()
    parents = [kls for kls in model_types if not kls._meta.abstract][::-1]
    pnames = [str(kls._meta.verbose_name_plural) for kls in parents]
    pcts = [ContentType.objects.get_for_model(mod) for mod in parents]
    base_url = "/".join(pnames)
    tag = pnames[-1]
    hash_url = tag
    try:
        static_tags = cls.static_tags() + [tag]
        hash_url = "*$".join(static_tags)
        print("static tags == ", static_tags)
    except AttributeError:
        pass
    SearchIndex.create_or_update(
        name=tag, return_url=base_url, hash_value=hash_url, in_department="products"
    )
    manufacturers = Manufacturer.objects.all()
    for manu in manufacturers:
        count = cls.objects.filter(manufacturer__label=manu.label).count()
        if not count > 0:
            continue
        newTag = f"{manu.label} {tag}"
        searchUrl = f"{base_url}?manufacturer={manu.pk}"
        newHash = f"{hash_url}*${manu.label}"
        SearchIndex.create_or_update(
            name=newTag, return_url=searchUrl, hash_value=newHash, in_department=tag
        )


def __create_static_indexes():
    bottom_list = []
    for cls in ProductSubClass.__subclasses__():
        subs = cls.__subclasses__()
        if not subs:
            bottom_list.append(cls)
            continue
        for sub in subs:
            bottom_list.append(sub)
    for kls in bottom_list:
        __create_tree_index(kls)


def __create_fs_indexes():
    all_si = SearchIndex.objects.all()
    all_si.delete()
    all_fs: List[FinishSurface] = FinishSurface.subclasses.select_related(
        "manufacturer"
    ).all().select_subclasses()
    count = 0
    for fin in all_fs:
        name = fin.get_name()
        vb_name = fin._meta.verbose_name_plural
        hash_tag = fin.tags() + [str(vb_name)]
        tag = list(set(hash_tag))
        tag = "$*".join(tag)
        qstring = "product-detail/" + str(fin.pk)
        count += 1
        try:
            SearchIndex.create_or_update(name=name, hash_value=tag, return_url=qstring)
        except (IntegrityError, TransactionManagementError):
            print("!!!!-----------error---------------!!!!")
            continue

    # print(base_url)
    # model = ContentType.objects.get_for_model(cls)
    # pnames = [kls._meta.verbose_name_plural for kls in parents]
    # parents = [ContentType.objects.get_for_model(mod) for mod in model_types]
    # print(pnames)


# static = [
#     {
#         'name': 'hardwood floors',
#         'tags': ['wood', 'hardwood', 'floors'],
#         'return': 'products/finish surfaces/hardwood'
#     },
#     {

#     }
# ]


# product_tree = ConfigTree.load().product_tree
# product_tree: Tree = __init_trees(product_tree)
# __crawl_tree(product_tree)

# for group in static:
#     tags = group.get('tags')
#     tag = '$*'.join(tags)
#     name = group.get('name')
#     return_url = group.get('return')
#     SearchIndex.objects.create(
#             name=name,
#             hash_value=tag,
#             return_url=return_url
#             )


# def __crawl_tree(tree: Tree):
#     __create_tree_index(tree)
#     if tree.children:
#         for child in tree.children:
#             __crawl_tree(child)

# def __init_trees(**kwargs):
#     name = kwargs.get('name')
#     count = kwargs.get('count')
#     children = kwargs.get('children')
#     tree = Tree(name, count)
#     if children:
#         for child in children:
#             tree.children.append(__init_trees(child))
#     return tree


@app.task
def send_danger_log_message(pk):
    from .models import DangerLog

    dlog = DangerLog.objects.get(pk=pk)
    message = f"{dlog.message} ----- dlog number {pk}"
    email_obj = EmailMessage(
        subject="Danger",
        body=message,
        from_email="jford@bluesift.com",
        to="jford@bluesift.com",
    )
    email_obj.send()
    return f"dlog {pk} email sent"
