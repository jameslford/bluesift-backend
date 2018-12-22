
from django.contrib.gis.measure import D
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
    lk = 'look'
    shdvar = 'shade_variation'

    mat = 'material'
    submat = 'sub_material'
    fin = 'finish'
    surtex = 'surface_texture'
    surcoat = 'surface_coating'

    thicknesses = Product.objects.all().value_list('thickness')
    shade_varations = ShadeVariation.objects.all()
    looks = Look.objects.all()
    manufacturers = Manufacturer.objects.all()

    materials = Material.objects.all()
    finishes = Finish.objects.all()
    surface_textures = SurfaceTexture.objects.all()
    surface_coatings = SurfaceCoating.objects.all()
    sub_materials = SubMaterial.objects.all()

    radii = [5, 10, 20, 50, 100, 200]

    def __init__(self, query):
        self.query = query
        self.app_query, self.app_query_raw = self.refine_list(query, self.app)
        self.avail_query, self.avail_query_raw = self.refine_list(query, self.avail)
        self.loc_query, self.loc_query_raw = self.refine_list(query, self.loc)
        self.lk_query, self.lk_query_raw = self.refine_list(query, self.lk)
        self.manu_query, self.manu_query_raw = self.refine_list(query, self.manu)
        self.sze_query, self.sz_query_raw = self.refine_list(query, self.sze)
        self.shdvar_query, self.shdvar_query_raw = self.refine_list(query, self.shdvar)
        self.thk_query, self.thk_query_raw = self.refine_list(query, self.thk)
        self.mat_query, self.manu_query_raw = self.refine_list(query, self.mat)
        self.submat_query, self.submat_query_raw = self.refine_list(query, self.submat)
        self.fin_query, self.fin_query_raw = self.refine_list(query, self.fin)
        self.surtex_query, self.surtex_query_raw = self.refine_list(query, self.surtex)
        self.surcoat_query, self.surcoat_query_raw = self.refine_list(query, self.surcoat)
        self.bool_raw = self.avail_query_raw + self.app_query_raw
        self.zipcode = None
        self.radius = None

    def refine_list(self, keyword):
        queries_raw = [q for q in self.query if keyword in q]
        queries = [q.replace(keyword+'-', '') for q in queries_raw]
        return [queries_raw, queries]

    def filter_bools(self, products):
        for application in self.app_queries + self.avail_queries:
            if hasattr(Product, application):
                arg = {application: True}
                products = products.filter(**arg)
            else:
                self.bool_raw = [q for q in self.bool_raw if application not in q]

    def filter_location(self, products):
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

    def filter_attribute(self, products):
        standalones = [self.thk_query, self.shdvar_query, self.lk_query]

    def do_work(self):
        pass
