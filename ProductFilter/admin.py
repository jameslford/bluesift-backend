""" blah blah """
from django.contrib import admin
from django.contrib.postgres import fields as pg_fields
from django_json_widget.widgets import JSONEditorWidget
from ProductFilter.models import ProductFilter, QueryIndex, FacetOthersCollection

# Register your models here.

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
        'filter_dictionary',
        'sub_product_description',
        'sub_product_image'
    )
    # readonly_fields = ('filter_dictionary',)
    # formfield_overrides = {
    #     pg_fields.JSONField: {'widget': JSONEditorWidget},
    # }


@admin.register(QueryIndex)
class QueryIndexAdmin(admin.ModelAdmin):
    fields = (
        'query_dict',
        'query_path',
        'response',
        'dirty',
        'product_filter',
    )

    list_filter = ('query_path',)
    ordering = ('query_path',)

    formfield_overrides = {
        pg_fields.JSONField: {'widget': JSONEditorWidget},
    }


admin.site.register(FacetOthersCollection)
