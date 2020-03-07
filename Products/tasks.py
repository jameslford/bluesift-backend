from config.celery import app
from .models import ValueCleaner



# @app.task
# def add_detail_record(path, pk):
#     record: ViewRecord = ViewRecord.objects.filter(path=path).latest('recorded')
#     if record:
#         record.product_detail_pk = pk
#         record.save()


@app.task
def add_value_cleaner(product_class: str, field, new_value, old_value):
    ValueCleaner.create_or_update(product_class, field, new_value, old_value)
    return f'{field}, {new_value}'
