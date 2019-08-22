from SpecializedProducts.models import FinishSurface


PRODUCT_SUBCLASSES = {
    'FinishSurface': FinishSurface
}

def valid_subclasses():
    return list(PRODUCT_SUBCLASSES.values())
