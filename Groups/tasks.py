from config.celery import app
from Analytics.models import ViewRecord
from Groups.models import ProCompany, RetailerCompany


@app.task
def add_retailer_record(path, pk):
    record: ViewRecord = ViewRecord.objects.filter(path=path).latest('recorded')
    retailer = RetailerCompany.objects.filter(pk=pk).first()
    if record and retailer:
        if not record.product_detail_pk:
            record.product_detail_pk = pk
            record.save()


@app.task
def add_pro_record(path, pk):
    record: ViewRecord = ViewRecord.objects.filter(path=path).latest('recorded')
    pro_comp = ProCompany.objects.filter(pk=pk).first()
    if pro_comp and not record:
        if not record.product_detail_pk:
            record.product_detail_pk = pk
            record.save()
