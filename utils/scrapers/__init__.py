from . import viking, armstrong, crossville, floridatile, shaw, subzero

mapper = {
    'armstrong': armstrong.scrape,
    'crossville': crossville.scrape,
    'floridatile': floridatile.scrape,
    'shaw': shaw.scrape,
    'subzero': subzero.scrape,
    'viking': viking.scrape,
}


def route_scrape(manufacturer, category):
    func = mapper.get(manufacturer)
    if not func:
        raise Exception(f'{manufacturer} is not a valid manufacturer')
    func(category)
