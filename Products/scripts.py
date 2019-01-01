
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point
from operator import itemgetter

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
    'pool_linings'
    ]


class FilterSorter:
    app = 'application'
    avail = 'availability'
    loc = 'location'
    manu = 'manufacturer'
    sze = 'size'
    thk = 'thickness'
    acolor = 'actual_color'
    lk = 'look'
    shdvar = 'shade_variation'

    mat = 'material'
    submat = 'sub_material'
    fin = 'finish'
    surtex = 'surface_texture'
    surcoat = 'surface_coating'

    # determines whether or not to return material specific facets
    spec_mat_facet = False

    thicknesses = Product.objects.all().values_list('thickness')
    shade_varations = ShadeVariation.objects.all()
    looks = Look.objects.all()
    manufacturers = Manufacturer.objects.all()

    materials = Material.objects.all()
    finishes = Finish.objects.all()
    surface_textures = SurfaceTexture.objects.all()
    surface_coatings = SurfaceCoating.objects.all()
    sub_materials = SubMaterial.objects.all()

    radii = [5, 10, 20, 50, 100, 200]

    def __init__(self, query, request_url):
        self.query = query
        self.request_url = [q.replace('quer=', '') for q in request_url]
        self.order = list(reversed(request_url))
        self.app_query, self.app_query_raw = self.refine_list(self.app)
        self.avail_query, self.avail_query_raw = self.refine_list(self.avail)
        self.loc_query, self.loc_query_raw = self.refine_list(self.loc)
        self.lk_query, self.lk_query_raw = self.refine_list(self.lk)
        self.manu_query, self.manu_query_raw = self.refine_list(self.manu)
        self.sze_query, self.sze_query_raw = self.refine_list(self.sze)
        self.acolor_query, self.acolor_query_raw = self.refine_list(self.acolor)
        self.thk_query, self.thk_query_raw = self.refine_list(self.thk)
        self.mat_query, self.manu_query_raw = self.refine_list(self.mat)
        self.submat_query, self.submat_query_raw = self.refine_list(self.submat)
        self.shdvar_query, self.shdvar_query_raw = self.refine_list(self.shdvar)
        self.fin_query, self.fin_query_raw = self.refine_list(self.fin)
        self.surtex_query, self.surtex_query_raw = self.refine_list(self.surtex)
        self.surcoat_query, self.surcoat_query_raw = self.refine_list(self.surcoat)

        self.bool_raw = self.avail_query_raw + self.app_query_raw

        self.bools = [
            [self.avail_query, self.avail, avai_terms],
            [self.app_query, self.app, app_terms]
        ]

        self.standalones = {
            self.shdvar: [self.shdvar + '__label', self.shdvar_query],
            self.lk: [self.lk + '__label', self.lk_query],
            self.acolor: [self.acolor, self.acolor_query],
            self.thk: [self.thk, self.thk_query],
            self.sze: [self.sze, self.sze_query],
            self.manu: [self.manu + '__label', self.manu_query],
            self.submat: [self.submat + '__label', self.submat_query],
            self.fin: [self.fin + '__label', self.fin_query],
            self.surtex: [self.surtex + '__label', self.surtex_query],
            self.surcoat: [self.surcoat + '__label', self.surcoat_query]
        }
        self.zipcode = None
        self.radius = None
        self.legit_queries = []
        self.filter_response = []

    def refine_list(self, keyword):
        queries_raw = [q for q in self.query if keyword in q]
        queries = [q.replace(keyword+'-', '') for q in queries_raw]
        return [queries, queries_raw]

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

    def filter_location(self, products):
        if not self.loc_query:
            return products
        rad_raw = [q for q in self.loc_query if 'radius' in q]
        zip_raw = [q for q in self.loc_query if 'zip' in q]
        radius_raw = int(rad_raw[0].replace('radius-', ''))
        radius = D(mi=radius_raw)
        zipcode = zip_raw[0].replace('zipcode-', '')
        coords = Zipcode.objects.filter(code=zipcode).first().centroid.point
        self.radius = radius
        if coords:
            self.zipcode = zipcode
            products = products.filter(locations__distance_lte=(coords, radius))
            return products
        else:
            self.zipcode = 'error'
            return products

    def or_list_query(self, products, term_list):
        _products = products
        term = term_list[0]
        args = term_list[1]
        id_term = term.replace('__label', '')
        facet = {'name': id_term, 'values': []}
        # gets all possible unique values for that attribute
        values = Product.objects.values_list(term, id_term).distinct()
        values = [q for q in values if q[0]]
        values = sorted(values, key=itemgetter(0))
        for val, idt in values:
            search_term = {term: val}
            value = {
                'label': str(val),
                'count': products.filter(**search_term).count(),
                'enabled': False,
                'value': idt
            }
            if str(idt) in args:
                value['enabled'] = True
                self.legit_queries.append(f'{id_term}-{idt}')
            facet['values'].append(value)
        self.filter_response.append(facet)
        if args:
            first_search = {id_term: args[0]}
            new_prods = products.filter(**first_search)
            for arg in args[1:]:
                next_search = {id_term: arg}
                new_prods = new_prods | products.filter(**next_search)
            return new_prods
        return _products

        ''' filters products down more every pass, in reverse order. 
            so last query user entered is the first evaluated'''

    def filter_attribute(self, products):
        _products = products
        ordered_set = []
        for req in self.request_url:
            q = req.split('-')
            if q[0] not in ordered_set:
                ordered_set.append(q[0])
        for term in ordered_set:
            value = self.standalones.get(term, None)
            if value:
                _products = self.or_list_query(_products, value)
                del self.standalones[term]
        for stnd, values2 in self.standalones.items():
            _products = self.or_list_query(_products, values2)
        return _products


    def filter_materials_down(self, products):
        _products = products
        material = None
        if self.mat_query:
            material_key = self.mat_query[0]
            material = Material.objects.filter(id=material_key).first()
        if material:
            self.spec_mat_facet = True
            _products = products.filter(material=material)
        for sub in self.manu_subs:
            _products = self.or_list_query(_products, sub[1], sub[0])
        return _products

    def bool_facet(self, products):
        for cat in self.bools:
            queries, name, terms = cat
            print(queries)
            facet = {'name': name, 'values': []}
            for item in terms:
                search = {item: True}
                value = {
                    'label': item,
                    'count': products.filter(**search).count(),
                    'enabled': item in queries,
                    'value': item}
                facet['values'].append(value)
            self.filter_response.append(facet)

    def return_filter(self, products):
        self.bool_facet(products)
        return self.filter_response
