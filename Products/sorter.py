import decimal
from operator import itemgetter
from django.db.models import Min, Max, Q
from django.contrib.postgres.search import SearchVector
from django.contrib.gis.measure import D
from Addresses.models import Zipcode
from rest_framework.pagination import PageNumberPagination

# from Products.models import Product
# from django.contrib.gis.geos import Point


class FilterSorter:
    avail = 'availability'
    avai_terms = ['for_sale_in_store']
    loc = 'location'
    price = 'lowest_price'
    manu = 'manufacturer'

    def __init__(self, request, sub_class, page_size=24):
        request_url = request.GET.urlencode().split('&')
        request_url = [query for query in request_url if 'page' not in query]
        self.ordering_term = request.GET.get('order_term', None)
        self.query = request.GET.getlist('quer')
        self.search_terms = request.GET.getlist('search', None)
        self.request_url = [q.replace('quer=', '') for q in request_url]
        self.page = int(request.GET.get('page', 1))
        self.page_size = page_size
        self.sub_class = sub_class

        self.message = None
        self.keyterm_facet = False
        self.return_products = True
        self.legit_queries = []
        self.loaf_more = True

        self.zipcode = None
        self.radius = None

        self.min_price = None
        self.max_price = None
        self.is_priced = False

        self.avail_query, self.avail_query_raw = self.refine_list(self.avail)
        self.price_query, self.price_query_raw = self.refine_list(self.price)
        self.loc_query, self.loc_query_raw = self.refine_list(self.loc)
        self.manu_query, self.manu_query_raw = self.refine_list(self.manu)

        self.bool_query, self.bool_query_raw = [self.refine_list(q) for q in sub_class.bool_groups()['name']]
        self.keyterm_query, self.keyterm_query_raw = self.refine_list(sub_class.key_term())
        self.bool_groups = self.form_list()

        self.dependents = self.form_dict(self.sub_class.dependents(), '__label')
        self.fk_standalones = self.form_dict(self.sub_class.fk_standalones(), '__label')
        self.standalones = self.form_dict(self.sub_class.standalones())

        _products = sub_class.select_related('product').objects.all()
        _products = self.filter_search_terms(_products)
        _products = self.filter_location(_products)
        _products = self.filter_price(_products)
        _products = self.filter_bools(_products)
        _products = self.filter_attribute(_products)
        self.bool_facet(_products)
        self.product_count = _products.count()
        _products = self.order(_products)
        self.products = self.paginate_products(_products)
        self.legit_queries = ['quer=' + q for q in self.legit_queries]

    def refine_list(self, keyword):
        queries = [q.replace(keyword+'-', '') for q in self.query if keyword in q]
        queries_raw = [q for q in self.query if keyword in q]
        return [queries, queries_raw]

    def form_dict(self, group, option=''):
        key_dict = {}
        for q in group:
            query = self.refine_list(q)[0]
            key_dict[q] = [q + option, query]
        return key_dict

    def form_list(self, group):
        bg = []
        for q in self.sub_class.bool_groups():
            b_query = [self.refine_list(k)[0] for k in q['terms']]
            item_list = [b_query, q['name'], q['terms']]
            bg.append(item_list)
        avai_list = [self.avail_query, self.avail, self.avai_terms]
        bg.append(avai_list)
        return bg

    def filter_search_terms(self, products):
        if not self.search_terms:
            return products
        for term in self.search_terms:
            searched_prods = products.annotate(
                    search=SearchVector(
                        'product__name',
                        'product__manufacturer__label',
                        'product__manufacturer_style',
                        'product__manu_collection',
                        'product__manufacturer_search'
                    )
            ).filter(search=term)
        if not searched_prods:
            self.message = 'No results'
            self.return_products = False
            return []
        return searched_prods

    def filter_location(self, products):
        if not self.loc_query:
            return products
        rad_raw = [q for q in self.loc_query if 'radius' in q]
        zip_raw = [q for q in self.loc_query if 'zip' in q]
        if not (rad_raw and zip_raw):
            return products
        radius_raw = int(rad_raw[-1].replace('radius-', ''))
        radius = D(mi=radius_raw)
        zipcode = zip_raw[-1].replace('zipcode-', '')
        coords = Zipcode.objects.filter(code=zipcode).first().centroid.point
        self.radius = radius
        if not coords:
            self.zipcode = 'invalid zipcode'
            return products
        rad_query = 'location-radius-' + str(radius_raw)
        zip_query = 'location-zip-' + str(zipcode)
        self.legit_queries = self.legit_queries + [rad_query, zip_query]
        self.zipcode = zipcode
        new_products = products.filter(product__locations__distance_lte=(coords, radius))
        if not new_products:
            self.message = 'No results'
            self.return_products = False
            return products
        return new_products

    def filter_price(self, products):
        if not self.avail_query:
            return products
        price_agg = products.aggregate(Min('lowest_price'), Max('lowest_price'))
        self.min_price = price_agg['lowest_price__min']
        self.max_price = price_agg['lowest_price__max']
        self.total_price_range = [self.min_price, self.max_price]
        if not self.price_query:
            return products
        min_price = [q.replace('min-', '') for q in self.price_query if 'min' in q]
        max_price = [q.replace('max-', '') for q in self.price_query if 'max' in q]
        self.is_priced = True
        _products = products
        if min_price:
            min_price = decimal.Decimal(min_price[-1])
            self.min_price = min_price
            min_quer_string = 'lowest_price-min-' + str(min_price)
            self.legit_queries.append(min_quer_string)
            _products = products.filter(product__lowest_price__gte=min_price)
        if max_price:
            max_price = decimal.Decimal(max_price[-1])
            self.max_price = max_price
            max_quer_string = 'lowest_price-max-' + str(max_price)
            self.legit_queries.append(max_quer_string)
            _products = _products.filter(product__lowest_price__lte=max_price)
        if not _products:
            self.message = 'No results'
            self.return_products = False
            return products
        return _products

    def filter_bools(self, products):
        _products = products
        search_terms = {}
        for av_term in self.avail_query:
            search_terms['product__' + av_term] = True
        for term in self.bool_terms:
            if hasattr(self.sub_class, term):
                search_terms[term] = True
            else:
                self.bool_raw = [q for q in self.bool_raw if term not in q]
        _products = _products.filter(**search_terms)
        return _products

    def filter__attributes(self, products):
        key_object = None
        keyterm_dict = self.sub_class.key_term()
        if self.keyterm_query:
            self.keyterm_query = self.keyterm_query[-1]
            key_object = keyterm_dict['class'].objects.filter(id=self.keyterm_query).first()
            self.keyterm_facet = True
            keyterm_filter_term = {keyterm_dict['name']: key_object}
            products = products.filter(**keyterm_filter_term)
            # self.mat_query = []
        else:
            self.dependents_query = {}
        kt_dict = self.form_dict(keyterm_dict['name'])
        self.attribute_group = {**self.fk_standalones, **self.dependents, **self.standalones, **kt_dict}
        ordered_set = [q.split('-')[0] for q in self.request_url]
        ordered_set = set(ordered_set)
        for term in ordered_set:
            value = self.attribute_group.get(term, None)
            if value:
                products = self.or_list_query(products, value)
                del self.attribute_group[term]
        for stnd, value2 in self.attribute_group.items():
            products = self.or_list_query(products, value2)
        return products

    def or_list_query(self, products, term_list):

        '''Products have already been either been filtered to one material or none at all.
        this function gets a list of all possible values (label - if a field, and id) for the given term list(field)
        it then filters by id (id_term)'''

        term = term_list[0]
        args = term_list[1]
        id_term = term.replace('__label', '')
        products = products.select_related(id_term).all()
        # _products = products
        facet = {
            'name': id_term,
            'total_count': 0,
            'values': []
            }
        values = self.sub_class.objects.values_list(term, id_term).distinct()
        values = [q for q in values if q[0]]
        # sorts values for for each attribute(term), by label so that they are consistents
        values = sorted(values, key=itemgetter(0))
        for val, idt in values:
            search_term = {id_term: idt}
            # line below is expensive
            count = products.filter(**search_term).count()
            if count == 0:
                continue
            facet['total_count'] += count
            value = {
                'label': str(val),
                'count': count,
                'enabled': False,
                'value': idt,
            }
            if str(idt) in args:
                value['enabled'] = True
                self.legit_queries.append(f'{id_term}-{idt}')
            facet['values'].append(value)
        self.filter_response.insert(0, facet)
        if not args:
            return products
        q_objects = Q()
        for arg in args:
            q_objects |= Q(**{id_term: arg})
        new_prods = products.filter(q_objects)
        return new_prods

    def bool_facet(self, products):
        for cat in self.bool_groups:
            queries, name, terms = cat
            facet = {
                'name': name,
                'total_count': 2,
                'values': []}
            for item in terms:
                search = {item: True}
                value = {
                    'label': item,
                    'count': products.filter(**search).count(),
                    'enabled': item in queries,
                    'value': item}
                facet['values'].append(value)
            self.filter_response = [facet] + self.filter_response
        if self.avail_query:
            loc_facet = {
                'name': 'location',
                'values': [],
                'zipcode': self.zipcode,
            }
            for rad in self.radii:
                enabled = True if rad == self.radius else False
                rad_dic = {'radius': rad, 'enabled': enabled, 'label': 'Radius ' + str(rad)}
                loc_facet['values'].append(rad_dic)

            price_facet = {
                'name': 'price',
                'min': self.min_price,
                'max': self.max_price,
                'range_values': self.total_price_range,
                'values': [
                    {'label': 'Price', 'enabled': self.is_priced}
                ]
            }
            self.filter_response.insert(1, loc_facet)
            self.filter_response.insert(2, price_facet)

    def order(self, products):
        if self.ordering_term:
            return products.order_by(self.ordering_term)
        return products


    def paginate_products(self, products):
        start_page = self.page - 1
        product_start = start_page * self.page_size
        product_end = self.page * self.page_size
        if product_end > self.product_count:
            self.load_more = True
            return products[product_start:]
        else:
            return products[product_start:product_end]



