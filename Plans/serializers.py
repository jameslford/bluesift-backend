import serpy


class PlanSerializer(serpy.Serializer):
    name = serpy.Field()
    duration = serpy.Field()
    billing_recurrence = serpy.Field()
    rate = serpy.Field()
    location_threshold = serpy.Field()
