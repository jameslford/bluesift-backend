
from Scraper.initial_urls import *
from SpecializedProducts.models import Resilient, Hardwood, TileAndStone, LaminateFlooring

# armstrong = Manufacturer.objects.get_or_create(label='armstrong')[0]
# crossville = Manufacturer.objects.get_or_create(label='crossville')[0]
# floridatile = 'florida_tile'
subzero = 'subzero'
armstrong = 'armstrong'
crossville = 'crossville'
shaw = 'shaw'
viking = 'viking'


groups = [
    # [
    #     subzero,
    # ],
    # [
    #     viking,
    #     VIKING_RANGE,
    #     Range,
    #     'range'
    # ],
    [
        armstrong,
        ARMSTRONG_COMMERCIAL_VCT,
        Resilient,
        'commercial_vct'
    ],
    [
        armstrong,
        ARMSTRONG_COMMERCIAL_HETEROVINYL,
        Resilient,
        'commercial_heterovinyl'
    ],
    [
        armstrong,
        ARMSTRONG_COMMERCIAL_HOMOVINYL,
        Resilient,
        'commercial_homovinyl'
    ],
    [
        armstrong,
        ARMSTRONG_COMMERCIAL_RIGIDCORE,
        Resilient,
        'commercial_rigidcore'
    ],
    [
        armstrong,
        ARMSTRONG_COMMERCIAL_LVT,
        Resilient,
        'commercial_luxuryflooring'
    ],
    [
        armstrong,
        ARMSTRONG_RESIDENTIAL_ENGINEERED_TILE,
        TileAndStone,
        'residential_engineeredtile'
    ],
    [
        armstrong,
        ARMSTRONG_RESIDENTIAL_LVT,
        Resilient,
        'residential_lvt'
    ],
    [
        armstrong,
        ARMSTRONG_RESIDENTIAL_RIGIDCORE,
        Resilient,
        'residential_rigidcore'
    ],
    [
        armstrong,
        ARMSTRONG_RESIDENTIAL_VINYLSHEET,
        Resilient,
        'residential_vinylsheet'
    ],
    [
        armstrong,
        ARMSTRONG_RESIDENTIAL_RIGIDCORE,
        Resilient,
        'residential_vinyltile'
    ],
    [
        crossville,
        CROSSVILLE,
        TileAndStone,
        'tile'
    ],
    [
        shaw,
        SHAW_HARDWOOD,
        Hardwood,
        'hardwood'
    ],
    [
        shaw,
        SHAW_LAMINATE,
        LaminateFlooring,
        'laminate'
    ],
    [
        shaw,
        SHAW_RESILIENT,
        Resilient,
        'resilient'
    ],
    [
        shaw,
        SHAW_TILE,
        TileAndStone,
        'tile-and-stone'
    ],
]
