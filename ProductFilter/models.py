from django.db import models
from django.http import HttpRequest
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField, JSONField
from config.scripts.globals import PRODUCT_SUBCLASSES


def subclass_content_types():
    ct_choices = []
    for name, subclass in PRODUCT_SUBCLASSES.items():
        ct = ContentType.objects.get_for_model(subclass)
        kwargs = {'app_label': ct.app_label, 'model': ct.model}
        ct_choices.append(models.Q(**kwargs))
    query = ct_choices.pop()
    for ct_choice in ct_choices:
        query |= ct_choice
    return query

class QueryIndex(models.Model):
    query_string = models.CharField(max_length=1000)
    response = JSONField()
    product_filter = models.ForeignKey(
        'ProductFilter',
        on_delete=models.CASCADE,
        related_name='query_indexes'
    )
    created = models.DateTimeField(auto_now=True)
    last_retrieved = models.DateTimeField()
    times_accessed = models.PositiveIntegerField()

    class Meta:
        unique_together = ('query_string', 'product_filter')


class ProductFilter(models.Model):

    price = 'lowest_price'
    location = 'location'
    response = None
    sub_product = models.OneToOneField(
        ContentType,
        limit_choices_to=subclass_content_types(),
        on_delete=models.CASCADE
        )
    standalones = ArrayField(
        models.CharField(max_length=30)
        )
    bool_groups = JSONField()
    key_field = models.CharField(max_length=30)
    dependent_fields = ArrayField(
        models.CharField(max_length=30)
        )


    def get_content_model(self):
        return self.sub_product.model_class()

    def check_bools(self):
        for group in self.bool_groups:
            pass


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)



class Sorter:
    """ takes a request and returns a filter and product set """
    def __init__(self, product_filter: ProductFilter, request: HttpRequest):
        self.product_filter = product_filter
        self.query_index: QueryIndex = None
        self.request = request
        self.response = {
            'message': None,
            'filter': None,
            'products': None
        }
        self.__get_response()

    def __get_response(self, update=False):
        """primary method on sorter class, all thats needed to receive response

        Keyword Arguments:
            update {bool} -- only used in internal testing (default: {False})
        """
        if self.request.method != 'GET':
            self.response['message'] = 'Invalid request method'
            return
        query_params = self.request.GET.urlencode()
        query_index, created = QueryIndex.objects.get_or_create(
            query_string=query_params,
            product_filter=self.product_filter
            )
        if not created and not update:
            query_index.times_accessed += 1
            query_index.last_accessed = now()
            query_index.save()
            self.response = query_index.response
            return
        self.query_index = query_index
        self.__parse_query()

    def __parse_query(self):
        # time to enter the dragon
        pass

