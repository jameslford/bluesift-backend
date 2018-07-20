from django.core.management.base import BaseCommand, CommandError
from Products.models import Product, ProductType, Manufacturer, Application


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Application.objects.bulk_create([
                                        Application(area='Floor',id=1),
                                        Application(area='Wall',id=2),
                                        Application(area='Counter Top',id=3),
                                        Application(area='Roof', id=4),
                                        Application(area='Siding', id=5),
                                        ])

        Manufacturer.objects.bulk_create([
                                        Manufacturer(name='Daltile', id=1),
                                        Manufacturer(name='Procelanosa', id=2),
                                        Manufacturer(name='Mohawk', id=3),
                                        Manufacturer(name='ArmStrong', id=4),
                                        ])
        ProductType.objects.bulk_create([
                                        ProductType(material='Tile', unit='Square Foot', id=1),
                                        ProductType(material='Carpet', unit='Square Foot', id=2),
                                        ProductType(material='Metal', unit='Square Foot', id=3),
                                        ProductType(material='Wood', unit='Square Foot', id=4),
                                        ])
        floor = Application.objects.get(id=1)
        wall = Application.objects.get(id=2)
        counter = Application.objects.get(id=3)
        roof = Application.objects.get(id=4)

        daltile = Manufacturer.objects.get(id=1)
        porcelanosa = Manufacturer.objects.get(id=2)
        mohawk = Manufacturer.objects.get(id=3)
        armstrong = Manufacturer.objects.get(id=4)

        tile = ProductType.objects.get(id=1)
        carpet = ProductType.objects.get(id=2)
        metal = ProductType.objects.get(id=3)
        wood = ProductType.objects.get(id=4)




        golden_marble = Product.objects.create(name='Golden Marble', manufacturer=daltile, product_type=tile, image='https://www.dropbox.com/s/5io8aedyvii1ebm/DAL_G215_NewVenetianGold_Swatch.jpg?dl=0')
        golden_marble.application.add(floor)

        panache = Product.objects.create(name='Panache Grey', manufacturer=daltile, product_type=tile, image='https://www.dropbox.com/s/qtdldri72vxav58/100088091_3.jpg?dl=0')
        panache.application.add(floor, wall)

        frump = Product.objects.create(name='Gator Tile', manufacturer=daltile, product_type=tile, image='https://www.dropbox.com/s/jug3cr8221cdylw/100155607_1.jpg?dl=0')
        frump.application.add(floor, roof)

        gator = Product.objects.create(name='Fake Wood', manufacturer=mohawk, product_type=carpet, image='https://www.dropbox.com/s/g2yrtby6hthfyse/100161044_2.jpg?dl=0')
        gator.application.add(floor, counter)

        catalon = Product.objects.create(name='Catonlonian Rain', manufacturer=mohawk, product_type=carpet, image='https://www.dropbox.com/s/hpe1k5tnwne1peh/100161120_1.jpg?dl=0')
        catalon.application.add(floor, counter, wall)

        mast = Product.objects.create(name='Brazilain Ebony', manufacturer=mohawk, product_type=carpet, image='https://www.dropbox.com/s/xwjhnobp06j1hhm/100161123_1.jpg?dl=0')
        mast.application.add(wall, roof)

        tadon = Product.objects.create(name='Dominican Hatch', manufacturer=mohawk, product_type=carpet, image='https://www.dropbox.com/s/bezczwngij3z2jz/100226594.jpg?dl=0')
        tadon.application.add(wall, floor)

        rand = Product.objects.create(name='Harbor Port', manufacturer=mohawk, product_type=wood, image='https://www.dropbox.com/s/nl7lqvif5e9ck97/100224088.jpg?dl=0')
        rand.application.add(floor, counter)

        tendon = Product.objects.create(name='Reclaimed Dresser', manufacturer=porcelanosa, product_type=wood, image='https://www.dropbox.com/s/qwvajhi0jghsx7a/DTN_M313_ConWht_WdgPol.jpg?dl=0')
        tendon.application.add(counter)

        lig = Product.objects.create(name='Bruised Apple', manufacturer=porcelanosa, product_type=wood, image='https://www.dropbox.com/s/dk224n5gp37u5ye/DAL_BA32_2x4_Msc_Grey.jpg?dl=0')
        lig.application.add(roof)

        trim = Product.objects.create(name='Swiss Delight', manufacturer=porcelanosa, product_type=metal, image='https://www.dropbox.com/s/56gbbhjjlygd6iv/DAL_G329_SapphireBlue_Swatch.jpg?dl=0')
        trim.application.add(floor)

        tart = Product.objects.create(name='Monkey Nut', manufacturer=porcelanosa, product_type=metal, image='https://www.dropbox.com/s/hycstshtifkd8y7/DTN_M313_ConWht_Pol.jpg?dl=0')
        tart.application.add(floor)

        


