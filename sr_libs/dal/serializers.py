from rest_framework import serializers


def create_dynamic_serializer(
    resource_model=None, allowed_fields="__all__", custom_serializer=None
):
    if custom_serializer:
        return custom_serializer  # just use it directly

    if resource_model is None:
        raise ValueError("Either resource_model or custom_serializer must be provided.")

    if allowed_fields == "__all__":
        allowed_fields = [f.name for f in resource_model._meta.fields]

    model_field_names = {f.name for f in resource_model._meta.fields}
    _read_only_fields = ["id"]  # always include id
    for f in ["created_at", "updated_at"]:
        if f in model_field_names:
            _read_only_fields.append(f)

    class Meta:
        model = resource_model
        fields = allowed_fields
        read_only_fields = _read_only_fields

    attrs = {"Meta": Meta}

    return type(
        f"{resource_model.__name__}Serializer",
        (serializers.ModelSerializer,),
        attrs,
    )


class DerivedSerializer(serializers.Serializer):
    """
    Base class for derived resources (no underlying model).
    Only requires list_data(filters) to be overridden.
    """

    @classmethod
    def list_data(cls, filters):
        raise NotImplementedError(
            f"{cls.__name__}.list_data(filters) not implemented! "
            "Override this method in your derived serializer."
        )
