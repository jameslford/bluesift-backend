from .base import BaseFacet, BaseReturnValue
from django.db.models import Q, Count



class FileTypeFacet(BaseFacet):

    class Meta:
        proxy = True


    def filter_self(self):
        if not self.qterms:
            return None
            # return self.return_stock()
        q_object = Q()
        if not isinstance(self.qterms, list):
            return None
        for term in self.qterms:
            arg = f'{self.attribute}__isnull'
            q_object |= Q(**{arg: False})
            self.selected = True
        self.queryset = self.model.objects.filter(q_object).values_list('pk', flat=True)
        return self.queryset
