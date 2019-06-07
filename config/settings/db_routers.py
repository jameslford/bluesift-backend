class ScraperRouter:

    def db_for_read(self, model, **hints):

        if 'ScraperCleaner' == model._meta.app_label:
            return 'scraper_default'
        if 'Scraper' in model._meta.app_label:
            instance = hints.get('instance', None)
            if not instance:
                return 'scraper_revised'
            return instance._state.db
        return None

    def db_for_write(self, model, **hints):

        if model._meta.app_label == 'ScraperCleaner':
            return 'scraper_default'
        if 'Scraper' in model._meta.app_label:
            instance = hints.get('instance', None)
            if not instance:
                return 'scraper_revised'
            return instance._state.db
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        if app_label == 'ScraperCleaner':
            if db == 'scraper_default':
                return True
            return False
        if db in ('scraper_default', 'scraper_revised'):
            if 'Scraper' in app_label:
                return True
            return False
        if 'Scraper' in app_label:
            return False
        return True
