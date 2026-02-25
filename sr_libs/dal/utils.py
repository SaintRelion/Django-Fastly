from django.core.exceptions import FieldDoesNotExist
from django.db import models


def apply_dynamic_filters(qs, model, query_params):
    filter_kwargs = {}

    for key, value in query_params.items():
        value = value.strip('"')

        try:
            field = model._meta.get_field(key)
        except FieldDoesNotExist:
            # allow lookup expressions like due_date__gte
            base_field = key.split("__")[0]
            try:
                model._meta.get_field(base_field)
            except FieldDoesNotExist:
                continue  # skip invalid fields

        # Handle ForeignKey fields
        if isinstance(field, models.ForeignKey):
            key = f"{key}_id"
            # handle comma-separated FKs
            if "," in value:
                value = [int(v) for v in value.split(",")]
                filter_kwargs[f"{key}__in"] = value
                continue
            else:
                value = int(value)  # single FK
                filter_kwargs[key] = value
                continue

        # Handle comma-separated values for non-FK fields
        if "," in value:
            filter_kwargs[f"{key}__in"] = value.split(",")
        else:
            filter_kwargs[key] = value

    if filter_kwargs:
        qs = qs.filter(**filter_kwargs)

    return qs
