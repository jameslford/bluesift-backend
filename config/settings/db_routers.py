class ScraperRouter:

    def db_for_read(self, model, **hints):

        if model._meta.app_label == 'Scraper':
            return 'scraper_default'
        return None

    def db_for_write(self, model, **hints):

        if model._meta.app_label == 'Scraper':
            return 'scraper_default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        if 'Scraper' in app_label:
            return bool(db == 'scraper_default' or db == 'scraper_revised')
        return None
