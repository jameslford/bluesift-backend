from config.celery import app
from Analytics.models import ViewRecord


@app.task
def add_retailer_record(path, pk):
    record: ViewRecord = ViewRecord.objects.filter(path=path).latest('recorded')
    if record:
        record.supplier_pk = pk
        record.save()
        return
    print('no record found')


@app.task
def add_pro_record(path, pk):
    record: ViewRecord = ViewRecord.objects.filter(path=path).latest('recorded')
    if record:
        record.product_detail_pk = pk
        record.save()
