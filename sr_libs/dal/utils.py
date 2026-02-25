from django.core.exceptions import FieldDoesNotExist
from django.db import models


def apply_dynamic_filters(qs, model, query_params):
    filter_kwargs = {}
    print(query_params)

    for key, value in query_params.items():
        # If value is a list, take the first element
        if isinstance(value, list):
            value = value[0]

        try:
            field = model._meta.get_field(key)
        except FieldDoesNotExist:
            continue  # skip unknown fields

        # ForeignKey -> use _id
        if isinstance(field, models.ForeignKey):
            key = f"{key}_id"

        filter_kwargs[key] = value

    if filter_kwargs:
        qs = qs.filter(**filter_kwargs)

    return qs
