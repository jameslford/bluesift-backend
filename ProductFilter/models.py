from django.db import models
from django.http import HttpRequest
from django.core import exceptions
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
    content_model = None
    sub_product = models.OneToOneField(
        ContentType,
        limit_choices_to=subclass_content_types(),
        on_delete=models.CASCADE
        )
    standalones = ArrayField(
        models.CharField(max_length=30, blank=True),
        null=True,
        blank=True
        )
    bool_groups = JSONField(blank=True, null=True)
    key_field = models.CharField(max_length=30, null=True, blank=True)
    dependent_fields = ArrayField(
        models.CharField(max_length=30, blank=True),
        null=True,
        blank=True
        )
    filter_dictionary = JSONField(blank=True, null=True)

    def get_content_model(self):
        if not self.content_model:
            self.content_model = self.sub_product.model_class()
        return self.content_model

    def check_value(self, name, fieldname: str = None):
        mymodel = self.get_content_model()
        try:
            field = mymodel._meta.get_field(name)
            if fieldname and type(field).__name__ != fieldname:
                return False
            return True
        except exceptions.FieldDoesNotExist:
            return False

    def check_bools(self):
        if not self.bool_groups:
            return
        for group_count, group in enumerate(self.bool_groups):
            for key in group.keys():
                if key != ('values' or 'name'):
                    del group[key]
            values = group.get('values', None)
            if not values:
                del self.bool_groups[group_count]
                continue
            for count, value in enumerate(values):
                if not self.check_value(value, 'BooleanField'):
                    del values[count]

    def check_keyterm(self):
        if not self.check_value(self.key_field):
            self.key_field = None

    def check_standalones(self):
        for count, standalone in enumerate(self.standalones):
            if not self.check_value(standalone):
                del self.standalones[count]

    def check_dependents(self):
        for count, dependent in enumerate(self.dependent_fields):
            if not self.check_value(dependent):
                del self.dependent_fields[count]

    def save(self, *args, **kwargs):
        self.check_bools()
        self.check_keyterm()
        self.check_standalones()
        self.check_dependents()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_content_model().__name__ + ' Filter'


class Facet:
    pass


class Sorter:
    """ takes a request and returns a filter and product set """
    def __init__(self, product_filter: ProductFilter, request: HttpRequest, update=False):
        self.product_filter = product_filter
        self.query_index: QueryIndex = None
        self.request = request
        self.response = {
            'message': None,
            'filter': None,
            'products': None
        }
        self.__get_response(update)

    def __get_response(self, update=False):
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
        self.__parse_request()

    def __parse_request(self):
        query = self.request.GET.getlist('quer', None)
        page = int(self.request.GET.get('page', 1))
        search = self.request.GET.getlist('search', None)
        ordering_term = self.request.GET.get('order_term', None)
        # if query:
        #     pass
        # if search:
        #     pass
        # if ordering_term:
        #     pass

    def __refine_list(self, keyword):
        pass

    def __parse_query(self, query: list):
        blah = []
        for blee in blah:
            name = blee['group_name']
            q_terms = [q for q in query if name in q]
            blee['q_terms'] = q_terms


    def __filter_products(self):
        products = self.product_filter.get_content_model().objects.all()

