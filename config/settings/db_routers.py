class ScraperRouter:

    def db_for_read(self, model, **hints):

        if 'Scraper' in model._meta.app_label:
            return 'scraper_revised'
        return None

    def db_for_write(self, model, **hints):

        if 'Scraper' in model._meta.app_label:
            return 'scraper_revised'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        if db in ('scraper_default', 'scraper_revised'):
            if 'Scraper' in app_label:
                return True
            return False
        if 'Scraper' in app_label:
            return False
        return True
