from ..models import ScraperFinishSurface
from config.scripts.measurements import clean_value

def get_special(product: ScraperFinishSurface, item):
    product.floors = True
    product.width = clean_value(item['PlankWidth'])
    product.length = clean_value(item['PlankLength'])
    product.thickness = clean_value(item['Thickness'])

    product.install_type = item['InstallationType']
    product.shade_variation = item['ColorVariationRatingShortDesc']
    gloss = None
    gloss_level = item['GlossLevel']
    if gloss_level:
        if gloss_level < 20:
            gloss = 'matte'
        elif gloss_level < 56:
            gloss = 'semi-gloss'
        else:
            gloss = 'high gloss'
    product.finish = gloss
    construction = item['Construction']
    if construction:
        product.material = construction + ' hardwood'
    else:
        product.material = 'hardwood'
    product.sub_material = item['Species']
    return product
