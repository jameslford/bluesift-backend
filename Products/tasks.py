from config.celery import app
from Analytics.models import ViewRecord
from .models import ValueCleaner, Product



@app.task
def add_detail_record(path, pk):
    record: ViewRecord = ViewRecord.objects.filter(path=path).latest('recorded')
    if record:
        record.product_detail_pk = pk
        record.save()


@app.task
def add_value_cleaner(pks, field, new_value):
    for pk in pks:
        product = Product.objects.get(pk=pk)
        vc, created = ValueCleaner.objects.get_or_create(
            product=product,
            field=field,
            new_value=new_value
            )
        return f'{vc.field}, {vc.new_value}, {created}'
