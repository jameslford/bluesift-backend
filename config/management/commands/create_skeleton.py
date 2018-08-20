from django.core.management.base import BaseCommand, CommandError
from Products.models import Manufacturer, Category, Look, Material, Build


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        carpet = Category.objects.create(label='Carpet')
        wood = Category.objects.create(label='Wood')
        stone = Category.objects.create(label='Stone & Glass')
        synthetics = Category.objects.create(label='Sythetics')

        sf = 'Square Feet'

        manufacturers = [
                        'Daltile',
                        'Crossville',
                        'Emser',
                        'Shaw',
                        'Mohawk',
                        'Wilsonart',
                        'Formica',
                        'ArmStrong',
                        'Beauflor',
                        'Porcelanosa'
        ]

        species = [ 
                    'Acacia', 
                    'Ash', 
                    'Birch', 
                    'Hickory', 
                    'Maple', 
                    'Oak', 
                    'Pine', 
                    'Walnut'
                ] 

        stones = [
                    'Ceramic',
                    'Glass',
                    'Granite',
                    'Limestone',
                    'Marble',
                    'Mixed'
                    'Porcelain',
                    'Quartz',
                    'Slate',
                    'Travertine',
        ]

        carpets = [
                    'SmartStrand',
                    'SmartStrand Silk',
                    'SmartStrand Silk Reserve',
                    'Air.O',
                    'Forever Fresh Ultrasoft',
                    'Wear-Dated',
                    'Everstrand',
                    'PermaStrand',
                    'Cleartouch Polyester',
                    'Endurance',
                    'R2X Nylon',
                    'Stainmaster Nylon'
        ]

        wood_builds = [ 'Solid', 'Engineered' ]

        stone_builds = ['Tile', 'Slab', 'Mosaic']

        carpet_builds = ['Twist', 'Loop', 'Textured', 'Pattern']

        synthetic_builds = [
                            'VCT (Vinyl Composite Tile)',
                            'LVT (Luxury Vinyl Tile)',
                            'Vinyl Sheet',
                            'Laminate Flooring',
                            'Solid Surface',
                            'Cabinet Laminate',
                            'Linoleum',
                            'Rigid Core',
                            ]

        for spec in species:
            Material.objects.create(category=wood, label=spec)

        for build in wood_builds:
            Build.objects.create(category=wood,label=build, unit=sf)

        for st in stones:
            Material.objects.create(category=stone, label=st)

        for build in stone_builds:
            Build.objects.create(category=stone, label=build, unit=sf)

        for strand in carpets:
            Material.objects.create(category=carpet, label=strand)

        for build in carpet_builds:
            Build.objects.create(category=carpet, label=build)

        for build in synthetic_builds:
            Build.objects.create(category=synthetics, label=build)

        for manu in manufacturers:
            Manufacturer.objects.create(name=manu)