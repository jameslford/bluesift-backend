from django.apps import AppConfig


class ProductFilterConfig(AppConfig):
    name = 'ProductFilter'

    def ready(self):
        import ProductFilter.signals
        super().ready()
