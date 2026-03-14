from typing import TypedDict, Union, Literal, Optional, Type
from rest_framework.serializers import Serializer
from rest_framework.permissions import BasePermission
from typing import Type, List

OperationKey = Literal["list", "retrieve", "create", "update", "delete", "archive"]

OperationValue = Union[bool, Literal["__all__"], Type[Serializer]]


class OperationsDict(TypedDict, total=False):
    list: OperationValue
    retrieve: OperationValue
    create: OperationValue
    update: OperationValue
    delete: OperationValue
    archive: OperationValue


PermissionValue = List[Type[BasePermission]]


class PermissionsDict(TypedDict, total=False):
    list: PermissionValue
    retrieve: PermissionValue
    create: PermissionValue
    update: PermissionValue
    delete: PermissionValue
    archive: PermissionValue


AuthenticatorValue = List[Literal[None]] | list


class AuthenticatorsDict(TypedDict, total=False):
    list: AuthenticatorValue
    retrieve: AuthenticatorValue
    create: AuthenticatorValue
    update: AuthenticatorValue
    delete: AuthenticatorValue
    archive: AuthenticatorValue
