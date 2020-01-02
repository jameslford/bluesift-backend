# from config.celery import app
# from Analytics.models import ViewRecord
# from UserProducts.models import RetailerLocation


# @app.task
# def add_retailer_record(path, pk):
#     record: ViewRecord = ViewRecord.objects.filter(path=path).latest('recorded')
#     retailer = RetailerLocation.objects.filter(pk=pk).first()
#     if record and retailer:
#         if not record.supplier_pk:
#             record.supplier_pk = pk
#             record.save()
