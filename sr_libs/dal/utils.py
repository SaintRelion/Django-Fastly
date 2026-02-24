from django.core.exceptions import FieldDoesNotExist
from django.db import models


def apply_dynamic_filters(qs, model, query_params):
    """
    Applies dynamic filtering based on query_params.
    - Skips unknown fields
    - Converts FK fields to _id
    - Supports comma-separated values (__in)
    """

    filter_kwargs = {}

    for key, value in query_params.items():
        value = value.strip('"')

        try:
            field = model._meta.get_field(key)

            # Convert FK to underlying id field
            if isinstance(field, models.ForeignKey):
                key = f"{key}_id"

        except FieldDoesNotExist:
            # Allow lookup expressions like due_date__gte
            base_field = key.split("__")[0]

            try:
                model._meta.get_field(base_field)
            except FieldDoesNotExist:
                continue  # skip invalid fields

        # Handle comma-separated values (__in)
        if "," in value:
            filter_kwargs[f"{key}__in"] = value.split(",")
        else:
            filter_kwargs[key] = value

    if filter_kwargs:
        qs = qs.filter(**filter_kwargs)

    return qs
