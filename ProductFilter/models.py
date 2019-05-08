from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from config.scripts.globals import PRODUCT_SUBCLASSES


def subclass_content_types():
    ct_choices = []
    for name, subclass in PRODUCT_SUBCLASSES.items():
        ct = ContentType.objects.get_for_model(subclass)
        taken = ProductFilter.objects.filter(subproduct=ct).first()
        if not taken:
            ct_choices.append(ct)
    return ct_choices


class ProductFilter(models.Model):
    sub_product = models.OneToOneField(
        ContentType,
        limit_choice_to=subclass_content_types(),
        on_delete=models.CASCADE
        )

class BaseFacet(models.Model):
    label = models.CharField(max_length=30)
    product_filter = models.ForeignKey(
        ProductFilter,
        on_delete=models.CASCADE,
        related_name='facets'
    )

    class Meta:
        abstract = True


class BoolFacet(models.Model):
    fields = ArrayField(
        models.CharField(max_length=40)
    )

    # write save methods for basefacet subclasses that make sure the
    # fields are on the model and of the rigght class per subclass
    # no need to have choices or select - just delete from arrayfield on save if not correct
    # other facets will no be grouped, but may have a special marker? ie price and range only if x

# class rangefacet - for length - width , maybe?

# class numberfacet - for thickness, price

# class geographyfacet - for geography

# class standardfacet - for charfields