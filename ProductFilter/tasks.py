from config.celery import app


@app.task
def add_facet_others_delay(qi_pk, facet_pk, intersection_pks):
    from ProductFilter.models import QueryIndex, FacetOthersCollection
    print('in celery qi_pk = ', str(qi_pk))
    query_index = QueryIndex.objects.filter(pk=qi_pk).first()
    if not query_index:
        return f'No QueryIndex for {qi_pk}'
    facet: FacetOthersCollection = FacetOthersCollection.objects.get_or_create(
        query_index=query_index,
        facet__pk=facet_pk
        )[0]
    facet.assign_new_products(intersection_pks)
    return f'FacetOthersCollection created for facet: {facet_pk}, and QueryIndex: {qi_pk}'
