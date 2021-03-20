Django Rest Framework Mango
===========================

A set of viewset mixin for the `Django REST
Framework. <https://www.django-rest-framework.org/>`__

Installation
------------

``pip install djangorestframework_mango``

Usage
-----

ActionMixin
~~~~~~~~~~~

It has six action methods that can be use instead of compare action with.

- is_create_action()
- is_retrieve_action()
- is_list_action()
- is_update_action()
- is_partial_update_action()
- is_destroy_action()

.. code:: python

    class ViewSet(ActionMixin, viewsets.GenericViewSet):
        queryset = Model.objects.all()
        serializer_class = ModelSerializer


        def get_queryset(self):
            queryset = super().get_queryset()

            if self.is_create_action:
                # change queryset for create
                queryset = queryset.change_for_create()
            elif self.is_retrieve_action():
                # change queryset for retrieve
                queryset = queryset.change_for_retrieve()
            elif self.is_list_action():
                # change queryset for list
                queryset = queryset.change_for_list()
            elif self.is_update_action():
                # change queryset for update
                queryset = queryset.change_for_update()
            elif self.is_partial_update_action():
                # change queryset for partial update
                queryset = queryset.change_for_partial_update()
            elif self.is_destroy_action():
                # change queryset for destroy
                queryset = queryset.change_for_destroy()

            return queryset

QuerysetMixin
~~~~~~~~~~~~~

It find action base queryset method and run it

.. code:: python

    class ViewSet(QuerysetMixin, viewsets.GenericViewSet):
        queryset = Model.objects.all()
        serializer_class = ModelSerializer

        # this method run automatically when this viewset gets create action
        def create_queryset(self, queryset):
            queryset = queryset.change_for_create()
            return queryset

        # this method run automatically when this viewset gets list action
        def list_queryset(self, queryset):
            queryset = queryset.change_for_list()
            return queryset

        # this method run automatically when this viewset gets retrieve action
        def retrieve_queryset(self, queryset):
            queryset = queryset.change_for_retrieve()
            return queryset
        # this method run automatically when this viewset gets update action
        def update_queryset(self, queryset):
            queryset = queryset.change_for_update()
            return queryset
        # this method run automatically when this viewset gets partial update action
        def partil_update_queryset(self, queryset):
            queryset = queryset.change_for_partial_update()
            return queryset
        # this method run automatically when this viewset gets destroy action
        def destroy_queryset(self, queryset):
            queryset = queryset.change_for_delete()
            return queryset

        # this method run automatically when this viewset gets update_extra_profile action
        def update_extra_profile_queryset(self, queryset):
            queryset = queryset.change_for_update_extra_profile()
            return queryset

        @action(methods['POST'], detail=True)
        def update_extra_profile(self, request, pk=None):
            # this method calls update_extra_profile_queryset() internally
            queryset = self.get_queryset()

            return Response(serializer.data)

SerializerMixin
~~~~~~~~~~~~~~~

You can define multi serializers by action

.. code:: python

    class ViewSet(QuerysetMixin, viewsets.GenericViewSet):
        queryset = Model.objects.all()
        serializer_class = ModelSerializer
        serializer_class_by_actions = {
            'create': {
                'v1': ModelCreateSerializerV1,
                'v2': ModelCreateSerializerV2,
                },
            'list': ModelListSerializer,
            'retrieve': ModelRetrieveSerializer,
            'update': ModelUpdateSerializer,
            'partial_update': ModelParitlaUpdateSerializer,
            'destory': ModelDestorySerializer,
            'update_extra_profile': ModelUpdateExtraProfileSerializer,
        }

        @action(methods['POST'], detail=True)
        def update_extra_profile(self, request, pk=None):
            # self.get_serializer returns ModelUpdateExtraProfileSerializer
            serializer = self.get_serializer()

            return Response(serializer.data)

PermissionMixin
~~~~~~~~~~~~~~~

You can define multi permissions by action

.. code:: python

    class ViewSet(QuerysetMixin, viewsets.GenericViewSet):
        queryset = Model.objects.all()
        serializer_class = ModelSerializer
        permission_by_actions = {
            'create': [Authenticated],
            'list': [ReadOnly],
            'retrieve': [AllowAny],
            'update': [Owner],
            'partial_update': [Owner],
            'destory': [Owner],
            'update_extra_profile': [Owner],
        }

        @action(methods['POST'], detail=True)
        def update_extra_profile(self, request, pk=None):
            # this method requires Owner permission
            serializer = self.get_serializer()

            return Response(serializer.data)

SessionMiddleware
~~~~~~~~~~~~~~~~~

You can use session data within request life cycle. - add
SessionMiddleware - use session from view, serializer and model

.. code:: python

    class ViewSet(viewsets.GenericViewSet):
        queryset = Model.objects.all()
        serializer_class = ModelSerializer

        def list_queryset(self, queryset):
            session = SessionMiddleware.get_session()
            session['current_user'] = self.request.user

            return queryset

    class Model(DjangoModel):

        @property
        def current_user(self):
            session = SessionMiddleware.get_session()
            session['current_user'] = self.request.user

            return session['current_user']


