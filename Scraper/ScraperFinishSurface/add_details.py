import decimal
from Scraper.ScraperFinishSurface.models import ScraperFinishSurface
from FinishSurfaces.models import FinishSurface
from django.contrib.postgres.fields import DecimalRangeField
from config.scripts.measurements import char_dec_range_conversion

REVISED_MODEL = ScraperFinishSurface
NEW_MODEL = FinishSurface


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
    name = (
        f'{revised_product.department_name()}_{new_product.manufacturer.label}_{new_product.manufacturer_sku}'
        f'{new_product.manu_collection}_{new_product.manufacturer_style}_'
        f'{new_product.material}_{new_product.sub_material}_{new_product.finish}_'
        f'{revised_product.width}x{revised_product.length}x{revised_product.thickness}'
    )
    new_product.name = name

    # new_product.width = char_dec_range_conversion(revised_product.width)
    # new_product.length = char_dec_range_conversion(revised_product.length)
    # new_product.thickness = char_dec_range_conversion(revised_product.thickness)
    new_product.save()
