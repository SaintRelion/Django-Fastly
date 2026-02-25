from django.core.exceptions import FieldDoesNotExist
from django.db import models


def apply_dynamic_filters(qs, model, query_params):
    filter_kwargs = {}

    for key, value in query_params.items():
        value = value.strip('"')

        try:
            field = model._meta.get_field(key)
        except FieldDoesNotExist:
            # Allow lookup expressions like due_date__gte
            base_field = key.split("__")[0]

            try:
                model._meta.get_field(base_field)
            except FieldDoesNotExist:
                continue  # skip invalid fields

        # Handle comma-separated values (__in)
        if isinstance(field, models.ForeignKey):
            key = f"{key}_id"
            value = int(value)  # ensure integer

        elif isinstance(field, models.CharField):
            filter_kwargs[f"{key}__iexact"] = value  # case-insensitive
            continue  # skip the exact filter below

        if "," in value:
            filter_kwargs[f"{key}__in"] = value.split(",")
        else:
            filter_kwargs[key] = value

    if filter_kwargs:
        qs = qs.filter(**filter_kwargs)

    return qs
