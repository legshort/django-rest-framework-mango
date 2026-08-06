from types import SimpleNamespace

import pytest
from django.core.exceptions import ImproperlyConfigured
from rest_framework import permissions, serializers, viewsets

from django_rest_framework_mango.mixins import (
    ActionMixin,
    MangoMixin,
    PermissionMixin,
    QuerysetMixin,
    SerializerMixin,
)


def build(viewset_class, action, **attrs):
    viewset = viewset_class()
    viewset.action = action
    for name, value in attrs.items():
        setattr(viewset, name, value)
    return viewset


class TestActionMixin:
    @pytest.mark.parametrize(
        'action,predicate',
        [
            ('create', 'is_create_action'),
            ('retrieve', 'is_retrieve_action'),
            ('list', 'is_list_action'),
            ('update', 'is_update_action'),
            ('partial_update', 'is_partial_update_action'),
            ('destroy', 'is_destroy_action'),
        ],
    )
    def test_predicate_matches_only_its_own_action(self, action, predicate):
        matching = build(type('V', (ActionMixin,), {}), action)
        other = build(type('V', (ActionMixin,), {}), 'something_else')

        assert getattr(matching, predicate)() is True
        assert getattr(other, predicate)() is False


class TestQuerysetMixin:
    class ViewSet(QuerysetMixin, viewsets.GenericViewSet):
        queryset = ['a', 'b', 'c']

        def list_queryset(self, queryset):
            return queryset[:1]

        def export_queryset(self, queryset):
            return queryset[:2]

    def test_hook_is_applied_for_its_action(self):
        assert build(self.ViewSet, 'list').get_queryset() == ['a']

    def test_custom_action_hook_is_applied(self):
        assert build(self.ViewSet, 'export').get_queryset() == ['a', 'b']

    def test_action_without_hook_passes_queryset_through(self):
        assert build(self.ViewSet, 'retrieve').get_queryset() == ['a', 'b', 'c']

    def test_create_hook_does_not_leak_into_other_actions(self):
        """Regression: `if self.is_create_action` (no parens) made create_queryset win every action."""

        class ViewSet(QuerysetMixin, viewsets.GenericViewSet):
            queryset = ['a', 'b', 'c']

            def create_queryset(self, queryset):
                return []

        assert build(ViewSet, 'list').get_queryset() == ['a', 'b', 'c']
        assert build(ViewSet, 'create').get_queryset() == []


class DefaultSerializer(serializers.Serializer):
    pass


class ListSerializer(serializers.Serializer):
    pass


class V1Serializer(serializers.Serializer):
    pass


class V2Serializer(serializers.Serializer):
    pass


class TestSerializerMixin:
    class ViewSet(SerializerMixin, viewsets.GenericViewSet):
        serializer_class = DefaultSerializer
        serializer_class_by_actions = {
            'list': ListSerializer,
            'create': {'v1': V1Serializer, 'v2': V2Serializer},
        }

    def test_action_mapping_is_used(self):
        assert build(self.ViewSet, 'list').get_serializer_class() is ListSerializer

    def test_unmapped_action_falls_back_to_serializer_class(self):
        assert build(self.ViewSet, 'retrieve').get_serializer_class() is DefaultSerializer

    def test_version_mapping_is_used(self):
        viewset = build(self.ViewSet, 'create', request=SimpleNamespace(version='v2'))

        assert viewset.get_serializer_class() is V2Serializer

    def test_version_mapping_without_versioning_raises(self):
        viewset = build(self.ViewSet, 'create', request=SimpleNamespace(version=None))

        with pytest.raises(ImproperlyConfigured):
            viewset.get_serializer_class()

    def test_viewset_without_mapping_uses_serializer_class(self):
        class ViewSet(SerializerMixin, viewsets.GenericViewSet):
            serializer_class = DefaultSerializer

        assert build(ViewSet, 'list').get_serializer_class() is DefaultSerializer


class TestPermissionMixin:
    class ViewSet(PermissionMixin, viewsets.GenericViewSet):
        permission_classes = [permissions.AllowAny]
        permission_by_actions = {'destroy': [permissions.IsAdminUser]}

    def test_action_mapping_is_used(self):
        permission_instances = build(self.ViewSet, 'destroy').get_permissions()

        assert [type(permission) for permission in permission_instances] == [permissions.IsAdminUser]

    def test_unmapped_action_falls_back_to_permission_classes(self):
        permission_instances = build(self.ViewSet, 'list').get_permissions()

        assert [type(permission) for permission in permission_instances] == [permissions.AllowAny]


def test_mango_mixin_combines_all_three():
    class ViewSet(MangoMixin, viewsets.GenericViewSet):
        queryset = ['a', 'b', 'c']
        serializer_class = DefaultSerializer
        permission_classes = [permissions.AllowAny]
        serializer_class_by_actions = {'list': ListSerializer}

        def list_queryset(self, queryset):
            return queryset[:1]

    viewset = build(ViewSet, 'list')

    assert viewset.get_queryset() == ['a']
    assert viewset.get_serializer_class() is ListSerializer
    assert [type(permission) for permission in viewset.get_permissions()] == [permissions.AllowAny]
