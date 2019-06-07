from django.test import TestCase
from Scraper.ScraperFinishSurface.models import ScraperFinishSurface
from Scraper.models import ScraperManufacturer, ScraperSubgroup, ScraperDepartment, ScraperCategory

class ScraperFinishSurfaceTestCase(TestCase):
    databases = {'scraper_default', 'default', 'scraper_revised'}

    def setUp(self):
        mohawk = ScraperManufacturer(name='mohawk')
        mohawk.save(using='scraper_default')
        finish_surface = ScraperDepartment(name='ScraperFinishSurface')
        finish_surface.save(using='scraper_default')
        default_finish_surface = ScraperDepartment.objects.using('scraper_default').get(pk=finish_surface.pk)
        category = ScraperCategory()
        category.department = default_finish_surface
        category.name = 'wood floors'
        category.save(using='scraper_default')
        subgroup = ScraperSubgroup(category=category, manufacturer=mohawk)
        subgroup.save(using='scraper_default')
        existing: ScraperFinishSurface = ScraperFinishSurface()
        existing.subgroup = subgroup
        existing.manufacturer_sku = '3fgt'
        existing.look = 'rhubarb'
        existing.save(using='scraper_default')

    def test_duplicate_fidelity(self):
        """ makes sure null values are updated but non null values are not overwritten """
        existing: ScraperFinishSurface = ScraperFinishSurface.objects.using('scraper_default').get(manufacturer_sku='3fgt')
        subgroup = ScraperSubgroup.objects.using('scraper_default').get(manufacturer__name='mohawk')
        new: ScraperFinishSurface = ScraperFinishSurface()
        new.manufacturer_sku = '3fgt'
        new.look = 'tomatoe'
        new.subgroup = subgroup
        new.commercial = True
        new.finish = 'honed'
        new.name_sku_check()
        self.assertEqual(existing.look, 'rhubarb')
        self.assertEqual(existing.commercial, True)
        self.assertEqual(existing.finish, 'honed')
