import decimal
from django.contrib.gis.measure import D
# from django.contrib.gis.geos import Point
from operator import itemgetter
from django.db.models import Min, Max, Q, Count
from django.contrib.postgres.search import SearchVector


from Addresses.models import Zipcode
from Products.models import (
    Product,
    Manufacturer,
    Look,
    Material,
    SubMaterial,
    ShadeVariation,
    Finish,
    SurfaceTexture,
    SurfaceCoating
)

avai_terms = [
    'for_sale_online',
    'for_sale_in_store'
    ]

app_terms = [
    'walls',
    'countertops',
    'floors',
    'cabinet_fronts',
    'shower_floors',
    'shower_walls',
    'exterior_walls',
    'exterior_floors',
    'covered_walls',
    'covered_floors',
    'pool_linings',
    'bullnose',
    'covebase',
    'corner_covebase'
    ]


class FilterSorter:
    app = 'application'
    avail = 'availability'
    loc = 'location'
    price = 'lowest_price'
    manu = 'manufacturer'
    sze = 'size'
    thk = 'thickness'
    acolor = 'actual_color'
    lcolor = 'label_color'
    lk = 'look'
    shdvar = 'shade_variation'
    mat = 'material'
    submat = 'sub_material'
    fin = 'finish'
    surtex = 'surface_texture'
    surcoat = 'surface_coating'

    # determines whether or not to return material specific facets
    spec_mat_facet = False

    # thicknesses = Product.objects.all().values_list('thickness')
    # shade_varations = ShadeVariation.objects.all()
    # looks = Look.objects.all()
    # manufacturers = Manufacturer.objects.all()

    # materials = Material.objects.all()
    # finishes = Finish.objects.all()
    # surface_textures = SurfaceTexture.objects.all()
    # surface_coatings = SurfaceCoating.objects.all()
    # sub_materials = SubMaterial.objects.all()

    radii = [5, 10, 20, 50, 100, 200]

    def __init__(self, query, search_terms, request_url):
        self.query = query
        self.search_terms = search_terms
        self.request_url = [q.replace('quer=', '') for q in request_url]
        self.app_query, self.app_query_raw = self.refine_list(self.app)
        self.avail_query, self.avail_query_raw = self.refine_list(self.avail)
        self.price_query, self.price_query_raw = self.refine_list(self.price)
        self.loc_query, self.loc_query_raw = self.refine_list(self.loc)
        self.lk_query, self.lk_query_raw = self.refine_list(self.lk)
        self.manu_query, self.manu_query_raw = self.refine_list(self.manu)
        self.lcolor_query, self.lcolor_query_raw = self.refine_list(self.lcolor)
        self.thk_query, self.thk_query_raw = self.refine_list(self.thk)
        self.mat_query, self.manu_query_raw = self.refine_list(self.mat)
        self.submat_query, self.submat_query_raw = self.refine_list(self.submat)
        self.fin_query, self.fin_query_raw = self.refine_list(self.fin)
        self.surcoat_query, self.surcoat_query_raw = self.refine_list(self.surcoat)
        # self.order = list(reversed(request_url))
        # self.sze_query, self.sze_query_raw = self.refine_list(self.sze)
        # self.acolor_query, self.acolor_query_raw = self.refine_list(self.acolor)
        # self.shdvar_query, self.shdvar_query_raw = self.refine_list(self.shdvar)
        # self.surtex_query, self.surtex_query_raw = self.refine_list(self.surtex)

        self.bool_raw = self.avail_query_raw + self.app_query_raw

        self.bools = [
            [self.app_query, self.app, app_terms],
            [self.avail_query, self.avail, avai_terms]
        ]

        self.standalones = {
            self.mat: [self.mat + '__label', self.mat_query],
            self.lk: [self.lk + '__label', self.lk_query],
            self.manu: [self.manu + '__label', self.manu_query],
            self.lcolor: [self.lcolor + '__label', self.lcolor_query],
            self.surcoat: [self.surcoat + '__label', self.surcoat_query],
            self.fin: [self.fin + '__label', self.fin_query],
            self.submat: [self.submat + '__label', self.submat_query],
            # self.thk: [self.thk, self.thk_query],
            # self.shdvar: [self.shdvar + '__label', self.shdvar_query],
            # self.sze: [self.sze, self.sze_query],
            # self.surtex: [self.surtex + '__label', self.surtex_query]
        }
        self.zipcode = None
        self.radius = None

        self.min_price = None
        self.max_price = None

        self.min_thick = None
        self.max_thick = None

        self.message = None
        self.return_products = True

        self.legit_queries = []
        self.filter_response = []

    def refine_list(self, keyword):
        queries_raw = [q for q in self.query if keyword in q]
        queries = [q.replace(keyword+'-', '') for q in queries_raw]
        return [queries, queries_raw]

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
        new_products = products.filter(locations__distance_lte=(coords, radius))
        if not new_products:
            self.message = 'No results'
            self.return_products = False
            return products
        return new_products


    def filter_price(self, products):
        price_agg = products.aggregate(Min('lowest_price'), Max('lowest_price'))
        self.min_price = price_agg['lowest_price__min']
        self.max_price = price_agg['lowest_price__max']
        self.total_price_range = [self.min_price, self.max_price]
        if not self.price_query:
            return products
        min_price = [q.replace('min-', '') for q in self.price_query if 'min' in q]
        max_price = [q.replace('max-', '') for q in self.price_query if 'max' in q]
        _products = products
        if min_price:
            min_price = decimal.Decimal(min_price[-1])
            self.min_price = min_price
            min_quer_string = 'lowest_price-min-' + str(min_price)
            self.legit_queries.append(min_quer_string)
            _products = products.filter(lowest_price__gte=min_price)
        if max_price:
            max_price = decimal.Decimal(max_price[-1])
            self.max_price = max_price
            max_quer_string = 'lowest_price-max-' + str(max_price)
            self.legit_queries.append(max_quer_string)
            _products = _products.filter(lowest_price__lte=max_price)
        if not _products:
            self.message = 'No results'
            self.return_products = False
            return products
        return _products

    def filter_bools(self, products):
        _products = products
        for application in self.app_query + self.avail_query:
            if hasattr(Product, application):
                arg = {application: True}
                _products = _products.filter(**arg)
            else:
                self.bool_raw = [q for q in self.bool_raw if application not in q]
        self.legit_queries = self.legit_queries + self.bool_raw
        return _products

    def or_list_query(self, products, term_list):

        '''Products have already been either been filtered to one material or none at all.
        this function gets a list of all possible values (label - if a field, and id) for the given term list(field)
        it then filters by id (id_term)'''

        term = term_list[0]
        args = term_list[1]
        id_term = term.replace('__label', '')
        products = products.select_related(id_term)
        # _products = products
        facet = {
            'name': id_term,
            'total_count': 0,
            'values': []
            }
        values = products.values_list(term, id_term).distinct()
        values = [q for q in values if q[0]]
        # sorts values for for each attribute(term), by label so that they are consistent
        values = sorted(values, key=itemgetter(0))
        for val, idt in values:
            search_term = {id_term: idt}
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
            # now convert list value to string and see if it was in the query to determine if enabled
            # enabled_test = str(idt)
            # if term == self.thk:
            #     enabled_test = enabled_test.rstrip('0')
            if str(idt) in args:
                value['enabled'] = True
                self.legit_queries.append(f'{id_term}-{idt}')
            facet['values'].append(value)
        self.filter_response.append(facet)
        if args:
            q_objects = Q()
            for arg in args:
                q_objects |= Q(**{id_term: arg})
            new_prods = products.filter(q_objects)
            return new_prods
            # first_search = {id_term: args[0]}
            # new_prods = products.filter(**first_search)
            # for arg in args[1:]:
            #     next_search = {id_term: arg}
            #     new_prods = new_prods | products.filter(**next_search)
            # return new_prods
        return products

    def filter_attribute(self, products):

        '''filters products down more every pass, in reverse order.
            so last query user entered is the first evaluated'''

        # _products = products
        # ordered_set = []
        material = None
        if self.mat_query:
            self.mat_query = self.mat_query[-1]
            material = Material.objects.filter(id=self.mat_query).first()
            self.spec_mat_facet = True
            products = products.filter(material=material)
            self.mat_query = []
        else:
            del self.standalones[self.fin]
            del self.standalones[self.submat]
            del self.standalones[self.surcoat]
        ordered_set = [q.split('-')[0] for q in self.request_url]
        ordered_set = set(ordered_set)
        # for req in self.request_url:
        #     q = req.split('-')
        #     if q[0] not in ordered_set:
        #         ordered_set.append(q[0])
        # filters in reverse order first
        for term in ordered_set:
            value = self.standalones.get(term, None)
            if value:
                products = self.or_list_query(products, value)
                del self.standalones[term]
        # then filters the remainder
        for stnd, values2 in self.standalones.items():
            products = self.or_list_query(products, values2)
        return products

    def bool_facet(self, products):
        for cat in self.bools:
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
            rad_values = []
            for rad in self.radii:
                enabled = True if rad == self.radius else False
                rad_dic = {'radius': rad, 'enabled': enabled}
                rad_values.append(rad_dic)
            loc_facet = {
                'name': 'location',
                'values': rad_values,
                'zipcode': self.zipcode,
            }
            price_facet = {
                'name': 'price',
                'min': self.min_price,
                'max': self.max_price,
                'range_values': self.total_price_range
            }
            # self.filter_response = [loc_facet, price_facet] + self.filter_response
            self.filter_response.insert(1, loc_facet)
            self.filter_response.insert(2, price_facet)

    def filter_thickness(self, products):
        thick_vals = products.aggregate(Min('thickness'), Max('thickness'))
        min_thick = thick_vals['thickness__min']
        max_thick = thick_vals['thickness__max']
        thk_facet = {
            'name': 'thickness',
            'min': float(min_thick),
            'max': float(max_thick),
            'range_values': [float(min_thick), float(max_thick)],
            'values': []
        }
        self.filter_response.append(thk_facet)
        if not self.thk_query:
            return products
        min_thk_query = [q.replace('min-', '') for q in self.thk_query if 'min' in q]
        max_thk_query = [q.replace('max-', '') for q in self.thk_query if 'max' in q]
        _products = products
        if min_thk_query:
            min_thick = decimal.Decimal(min_thk_query[-1])
            thk_facet['min'] = float(min_thick)
            self.legit_queries.append('thickness-min-' + str(min_thick))
            _products = _products.filter(thickness__gte=min_thick)
            thk_facet['values'] + [{'label': 'min_thickness ' + str(min_thick)}, {'enabled': True}]
        if max_thk_query:
            max_thick = decimal.Decimal(max_thk_query[-1])
            thk_facet['max'] = float(max_thick)
            self.legit_queries.append('thickness-max-' + str(max_thick))
            _products = _products.filter(thickness__lte=max_thick)
            thk_facet['values'] + [{'label': 'max_thickness ' + str(max_thick)}, {'enabled': True}]
        if not _products:
            self.message = 'No results'
            self.return_products = False
            return products
        return _products

    def return_filter(self, products):
        self.bool_facet(products)
        return self.filter_response

    def filter_search(self, products):
        if not self.search_terms:
            return products
        for term in self.search_terms:
            searched_prods = products.annotate(
                    search=SearchVector(
                        'name',
                        'manufacturer__label',
                        'manufacturer_color',
                        'manu_collection',
                        'material__label'
                    )
            ).filter(search=term)
        if not searched_prods:
            self.message = 'No results'
            self.return_products = False
            return []
        return searched_prods

