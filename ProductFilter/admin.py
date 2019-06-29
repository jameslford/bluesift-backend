from django.contrib import admin
from django.contrib.postgres import fields as pg_fields
from django_json_widget.widgets import JSONEditorWidget
from ProductFilter.models import ProductFilter, QueryIndex

# Register your models here.

# admin.site.register(ProductFilter)
@admin.register(ProductFilter)
class ProductFilterAdmin(admin.ModelAdmin):
    fields = (
        'sub_product',
        'bool_groups',
        'key_field',
        'color_field',
        'independent_multichoice_fields',
        'independent_range_fields',
        'dependent_fields',
        'filter_dictionary'
    )
    # readonly_fields = ('filter_dictionary',)
    formfield_overrides = {
        pg_fields.JSONField: {'widget': JSONEditorWidget},
    }

@admin.register(QueryIndex)
class QueryIndexAdmin(admin.ModelAdmin):
    fields = (
        'query_dict',
        'query_path',
        'response',
        'dirty',
        'product_filter',
        'products'
    )

    list_filter = ('query_path',)
    ordering = ('query_path',)

    formfield_overrides = {
        pg_fields.JSONField: {'widget': JSONEditorWidget},
    }
