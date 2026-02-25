from django.core.exceptions import FieldDoesNotExist
from django.db import models


def apply_dynamic_filters(qs, model, query_params):
    filter_kwargs = {}

    for key, value in query_params.items():
        try:
            field = model._meta.get_field(key)
        except FieldDoesNotExist:
            continue  # skip unknown fields

        # If it's a FK, filter by underlying _id
        if isinstance(field, models.ForeignKey):
            key = f"{key}_id"

        # Use value as-is (string), exact match
        filter_kwargs[key] = value

    if filter_kwargs:
        qs = qs.filter(**filter_kwargs)

    return qs
