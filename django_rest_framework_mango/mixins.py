from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, ClassVar

from django.core.exceptions import ImproperlyConfigured

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import QuerySet
    from rest_framework.permissions import _PermissionClass, _SupportsHasPermission
    from rest_framework.serializers import BaseSerializer
    from rest_framework.viewsets import GenericViewSet

    # action / request / serializer_class / permission_classes / get_queryset all come from here.
    _Base = GenericViewSet[Any]

    SerializerClass = type[BaseSerializer[Any]]
else:
    _Base = object


class ActionMixin:
    action: str

    def is_create_action(self) -> bool:
        return self.action == 'create'

    def is_retrieve_action(self) -> bool:
        return self.action == 'retrieve'

    def is_list_action(self) -> bool:
        return self.action == 'list'

    def is_update_action(self) -> bool:
        return self.action == 'update'

    def is_partial_update_action(self) -> bool:
        return self.action == 'partial_update'

    def is_destroy_action(self) -> bool:
        return self.action == 'destroy'


class QuerysetMixin(ActionMixin, _Base):
    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()

        # ponytail: one getattr replaces a per-action if/elif chain, custom @action hooks included.
        hook: Callable[[QuerySet[Any]], QuerySet[Any]] | None = getattr(self, f'{self.action}_queryset', None)

        return hook(queryset) if hook is not None else queryset


class SerializerMixin(_Base):
    serializer_class_by_actions: ClassVar[dict[str, SerializerClass | dict[str, SerializerClass]]] = {}

    def get_serializer_class(self) -> SerializerClass:
        serializer_class = self.serializer_class_by_actions.get(self.action)

        # ponytail: unmapped actions go back to DRF, which keeps its "set serializer_class" assert.
        if serializer_class is None:
            return super().get_serializer_class()

        if isinstance(serializer_class, dict):
            version = self.request.version
            if version is None:
                raise ImproperlyConfigured(
                    f'{type(self).__name__}.serializer_class_by_actions maps {self.action!r} by version, '
                    f'but no versioning scheme is configured.'
                )
            return serializer_class[version]

        return serializer_class


class PermissionMixin(_Base):
    permission_by_actions: ClassVar[dict[str, Sequence[_PermissionClass]]] = {}

    def get_permissions(self) -> Sequence[_SupportsHasPermission]:
        permission_classes = self.permission_by_actions.get(self.action)

        if permission_classes is None:
            return super().get_permissions()

        return [permission() for permission in permission_classes]


class MangoMixin(QuerysetMixin, SerializerMixin, PermissionMixin):
    pass
