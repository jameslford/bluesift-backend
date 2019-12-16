from config.celery import app
from Analytics.models import ViewRecord


@app.task
def add_detail_record(path, pk):
    record: ViewRecord = ViewRecord.objects.filter(path=path).latest('recorded')
    if record:
        record.product_detail_pk = pk
        record.save()
