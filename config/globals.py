from enum import Enum
from SpecializedProducts.models import FinishSurface

class BusinessType(Enum):
    RETAILER_LOCATION = 'retailer-location'
    RETAILER_COMPANY ='retailer-company'
    PRO_COMPANY = 'pro-company'

PRODUCT_SUBCLASSES = {
    'FinishSurface': FinishSurface
}

def valid_subclasses():
    return list(PRODUCT_SUBCLASSES.values())
