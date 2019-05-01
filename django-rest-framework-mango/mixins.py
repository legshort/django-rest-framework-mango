class ActionMixin:
    def is_create_action(self):
        return 'create' == self.action

    def is_retrieve_action(self):
        return 'retrieve' == self.action

    def is_list_action(self):
        return 'list' == self.action

    def is_update_action(self):
        return 'update' == self.action

    def is_partial_update_action(self):
        return 'partial_update' == self.action

    def is_destroy_action(self):
        return 'destroy' == self.action


class QuerysetMixin(ActionMixin):
    def get_queryset(self):
        queryset = super().get_queryset()

        if self.is_create_action and hasattr(self, 'create_queryset'):
            queryset = self.create_queryset(queryset)
        elif self.is_retrieve_action() and hasattr(self, 'retrieve_queryset'):
            queryset = self.retrieve_queryset(queryset)
        elif self.is_list_action() and hasattr(self, 'list_queryset'):
            queryset = self.list_queryset(queryset)
        elif self.is_update_action() and hasattr(self, 'update_queryset'):
            queryset = self.update_queryset(queryset)
        elif self.is_partial_update_action() and hasattr(self, 'partial_update_queryset'):
            queryset = self.partial_update_queryset(queryset)
        elif self.is_destroy_action() and hasattr(self, 'destroy_queryset'):
            queryset = self.destroy_queryset(queryset)
        elif hasattr(self, f'{self.action}_queryset'):
            queryset_method = getattr(self, f'{self.action}_queryset')
            queryset = queryset_method(queryset)

        return queryset


class SerializerMixin:
    def get_serializer_class(self):
        if hasattr(self, 'serializer_class_by_actions'):
            return self.serializer_class_by_actions.get(self.action, self.serializer_class)

        return self.serializer_class


class PermissionMixin:
    def get_permissions(self):
        permission_classes = self.permission_classes

        if hasattr(self, 'permission_by_actions'):
            permission_classes = self.permission_by_actions.get(self.action, self.permission_classes)

        return [permission() for permission in permission_classes]


class MangoMixin(QuerysetMixin, SerializerMixin, PermissionMixin):
    pass
