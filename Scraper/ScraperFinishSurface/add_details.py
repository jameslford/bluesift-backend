import decimal
from dataclasses import dataclass
from Scraper.ScraperFinishSurface.models import ScraperFinishSurface
from SpecializedProducts.models import FinishSurface
from config.scripts.measurements import char_dec_range_conversion

REVISED_MODEL = ScraperFinishSurface
NEW_MODEL = FinishSurface

class DimensionValue:
    def __init__(self, dimension: str):
        self.range = None
        self.absolute = None
        self.continuous = False
        self.convert_to_range(dimension)
        print(self.range)

    def return_split(self, val: str):
        if val:
            split = val.split('-')
            if len(split) > 1:
                self.continuous = True
                return split
        return [val, None]

    def convert_to_range(self, value: str):
        vals = self.return_split(value)
        return_vals = []
        for val in vals:
            if val and '/' in val:
                div_split = val.split('/')
                if len(div_split) > 2:
                    print('div split = ', div_split)
                    return_vals.append(None)
                    continue
                num, div = div_split
                try:
                    val = float(num) / float(div)
                except (ValueError, TypeError):
                    return_vals.append(None)
                    continue
            try:
                dec = float(val)
                dec = round(dec, 2)
                dec = decimal.Decimal(val)
                # dec = divisor * (round(dec, 2) / divisor)
                return_vals.append(dec)
            except (ValueError, TypeError):
                return_vals.append(None)
        if self.continuous:
            self.absolute = return_vals[-1]
        else:
            self.absolute = return_vals[0]
        self.range = return_vals


def add_details(new_product: NEW_MODEL, revised_product: REVISED_MODEL):
    new_product.material = revised_product.material
    new_product.sub_material = revised_product.sub_material
    new_product.finish = revised_product.finish
    new_product.surface_coating = revised_product.surface_coating
    new_product.look = revised_product.look
    new_product.shade_variation = revised_product.shade_variation

    new_product.shape = revised_product.shape
    new_product.label_color = revised_product.label_color

    new_product.edge = revised_product.edge
    new_product.end = revised_product.end

    new_product.install_type = revised_product.install_type
    new_product.sqft_per_carton = revised_product.sqft_per_carton

    new_product.walls = revised_product.walls
    new_product.floors = revised_product.floors
    new_product.countertops = revised_product.countertops
    new_product.cabinet_fronts = revised_product.cabinet_fronts
    new_product.exterior_walls = revised_product.exterior_walls
    new_product.exterior_floors = revised_product.exterior_floors
    new_product.shower_floors = revised_product.shower_floors
    new_product.shower_walls = revised_product.shower_walls
    new_product.covered_floors = revised_product.covered_floors
    new_product.covered_walls = revised_product.covered_walls
    new_product.bullnose = revised_product.bullnose
    new_product.covebase = revised_product.covebase
    new_product.pool_linings = revised_product.pool_linings
    new_product.width = DimensionValue(revised_product.width).range
    new_product.length = DimensionValue(revised_product.length).range
    new_product.thickness = DimensionValue(revised_product.thickness).absolute
    name = (
        f'{revised_product.department_name()}_{new_product.manufacturer.label}_{new_product.manufacturer_sku}'
        f'{new_product.manu_collection}_{new_product.manufacturer_style}_'
        f'{new_product.material}_{new_product.sub_material}_{new_product.finish}_'
        f'{revised_product.width}x{revised_product.length}x{revised_product.thickness}'
    )
    new_product.name = name
    new_product.save()


    # new_product.width = char_dec_range_conversion(revised_product.width)
    # new_product.length = char_dec_range_conversion(revised_product.length)
    # new_product.thickness = char_dec_range_conversion(revised_product.thickness)


    # class RangeValues:

#     def __init__(self, width: str, length: str, thickness: str):
#         self.width = DimensionValue(width)
#         self.length = DimensionValue(length)
#         self.thickness = DimensionValue(thickness)
#         self.size = self.get_size()

#     def get_size(self):
#         if self.width.continuous or self.length.continuous:
#             return 'continuous'
#         try:
#             sqft = self.width.absolute * self.length.absolute
#             if sqft < 144:
#                 return 'small'
#             if sqft < 


        # width = [x is not None for x in self.width]
        # if len(width) > 1:
        #     width = 'continuous'
        # length = [x is not None for x in self.length]
        # if len(length) > 1

        # if sum(x for x in self.width) > 1: