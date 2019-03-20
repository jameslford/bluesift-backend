import decimal
from operator import itemgetter
from django.db.models import Min, Max, Q
from django.contrib.postgres.search import SearchVector
from django.contrib.gis.measure import D
from Addresses.models import Zipcode
# from Products.models import Product
# from django.contrib.gis.geos import Point


class FilterSorter:
    avail = 'availability'
    loc = 'location'
    price = 'lowest_price'
    manu = 'manufacturer'

    def __init__(self, request, sub_class):
        request_url = request.GET.urlencode().split('&')
        request_url = [query for query in request_url if 'page' not in query]
        self.sub_class = sub_class

        self.message = None
        self.return_products = True

        self.ordering_term = request.GET.get('order_term', None)
        self.query = request.GET.getlist('quer')
        self.search_terms = request.GET.getlist('search', None)
        self.request_url = [q.replace('quer=', '') for q in request_url]

        self.avail_query = self.refine_list(self.avail)
        self.price_query = self.refine_list(self.price)
        self.loc_query = self.refine_list(self.loc)
        self.manu_query = self.refine_list(self.manu)

        self.bool_query = [self.refine_list(q) for q in sub_class.bool_groups()['name']]
        self.keyterm_query = self.refine_list(sub_class.key_term())
        self.dependents_query = [self.refine_list(q) for q in sub_class.dependents()]
        self.fk_standalones = [self.refine_list(q) for q in sub_class.fk_standalones()]
        self.standalones = [self.refine_list(q) for q in sub_class.standalones()]

        _products = sub_class.objects.all()
        _products = self.filter_search_terms(_products)
        _products = self.filter_location(_products)
        _products = self.filter_price(_products)

    def refine_list(self, keyword):
        queries = [q.replace(keyword+'-', '') for q in self.query if keyword in q]
        # queries = [q.replace(keyword+'-', '') for q in queries_raw]
        return queries

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
            search_terms[term] = True
        _products = _products.filter(**search_terms)
        return _products
        # else:
        #     self.bool_raw = [q for q in self.bool_raw if application not in q]
        # self.legit_queries = self.legit_queries + self.bool_raw

    def filter__attributes(self, products):
        pass
