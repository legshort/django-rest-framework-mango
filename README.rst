Django Rest Framework Mango
===========================

A set of viewset mixins for the `Django REST
Framework. <https://www.django-rest-framework.org/>`__

Fully type hinted — the package ships ``py.typed``, so your type checker
sees the mixin signatures.

Supported versions
------------------

============== =========================
Python         3.10, 3.11, 3.12, 3.13, 3.14
Django         5.2, 6.0
DRF            3.16+
============== =========================

Installation
------------

``pip install djangorestframework-mango``

Usage
-----

.. code:: python

    from django_rest_framework_mango.middlewares import SessionMiddleware
    from django_rest_framework_mango.mixins import (
        ActionMixin,
        MangoMixin,
        PermissionMixin,
        QuerysetMixin,
        SerializerMixin,
    )

ActionMixin
~~~~~~~~~~~

It has six action methods that can be used instead of comparing ``self.action``.

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

            if self.is_create_action():
                # change queryset for create
                queryset = queryset.change_for_create()
            elif self.is_retrieve_action():
                # change queryset for retrieve
                queryset = queryset.change_for_retrieve()
            elif self.is_list_action():
                # change queryset for list
                queryset = queryset.change_for_list()

            return queryset

QuerysetMixin
~~~~~~~~~~~~~

It finds the ``<action>_queryset`` method and runs it. Any action works,
including custom ``@action`` methods. Actions without a matching method
leave the queryset untouched.

.. code:: python

    class ViewSet(QuerysetMixin, viewsets.GenericViewSet):
        queryset = Model.objects.all()
        serializer_class = ModelSerializer

        # this method runs automatically when this viewset gets the create action
        def create_queryset(self, queryset):
            return queryset.change_for_create()

        # this method runs automatically when this viewset gets the list action
        def list_queryset(self, queryset):
            return queryset.change_for_list()

        # this method runs automatically when this viewset gets the partial update action
        def partial_update_queryset(self, queryset):
            return queryset.change_for_partial_update()

        # this method runs automatically when this viewset gets the update_extra_profile action
        def update_extra_profile_queryset(self, queryset):
            return queryset.change_for_update_extra_profile()

        @action(methods=['POST'], detail=True)
        def update_extra_profile(self, request, pk=None):
            # this method calls update_extra_profile_queryset() internally
            queryset = self.get_queryset()

            return Response(serializer.data)

SerializerMixin
~~~~~~~~~~~~~~~

You can define multiple serializers by action. Unmapped actions fall back
to ``serializer_class``.

.. code:: python

    class ViewSet(SerializerMixin, viewsets.GenericViewSet):
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
            'partial_update': ModelPartialUpdateSerializer,
            'destroy': ModelDestroySerializer,
            'update_extra_profile': ModelUpdateExtraProfileSerializer,
        }

        @action(methods=['POST'], detail=True)
        def update_extra_profile(self, request, pk=None):
            # self.get_serializer returns ModelUpdateExtraProfileSerializer
            serializer = self.get_serializer()

            return Response(serializer.data)

A nested dict maps by API version, so it requires a `versioning scheme
<https://www.django-rest-framework.org/api-guide/versioning/>`__ to be
configured — otherwise ``ImproperlyConfigured`` is raised.

PermissionMixin
~~~~~~~~~~~~~~~

You can define multiple permissions by action. Unmapped actions fall back
to ``permission_classes``.

.. code:: python

    class ViewSet(PermissionMixin, viewsets.GenericViewSet):
        queryset = Model.objects.all()
        serializer_class = ModelSerializer
        permission_by_actions = {
            'create': [IsAuthenticated],
            'list': [ReadOnly],
            'retrieve': [AllowAny],
            'update': [Owner],
            'partial_update': [Owner],
            'destroy': [Owner],
            'update_extra_profile': [Owner],
        }

        @action(methods=['POST'], detail=True)
        def update_extra_profile(self, request, pk=None):
            # this method requires Owner permission
            serializer = self.get_serializer()

            return Response(serializer.data)

MangoMixin
~~~~~~~~~~

``QuerysetMixin``, ``SerializerMixin`` and ``PermissionMixin`` combined.

.. code:: python

    class ViewSet(MangoMixin, viewsets.GenericViewSet):
        queryset = Model.objects.all()
        serializer_class = ModelSerializer
        serializer_class_by_actions = {'list': ModelListSerializer}
        permission_by_actions = {'destroy': [Owner]}

        def list_queryset(self, queryset):
            return queryset.change_for_list()

SessionMiddleware
~~~~~~~~~~~~~~~~~

Share data within a request life cycle — useful where the request is not
reachable, such as a model. The session is created per thread and cleared
when the request finishes, even if the view raises.

.. code:: python

    # settings.py
    MIDDLEWARE = [
        ...,
        'django_rest_framework_mango.middlewares.SessionMiddleware',
    ]

.. code:: python

    class ViewSet(QuerysetMixin, viewsets.GenericViewSet):
        queryset = Model.objects.all()
        serializer_class = ModelSerializer

        def list_queryset(self, queryset):
            SessionMiddleware.get_session()['current_user'] = self.request.user

            return queryset

    class Model(models.Model):

        @property
        def current_user(self):
            # the model cannot reach the request, so it reads what the view stored
            session = SessionMiddleware.get_session() or {}

            return session.get('current_user')

Development
-----------

Tests run against every supported Python and Django combination through
`tox <https://tox.wiki/>`__. ``tox-uv`` downloads the interpreters, so
none of them need to be installed beforehand.

.. code:: bash

    uvx --with tox-uv tox                # every combination
    uvx --with tox-uv tox -f py314       # Python 3.14 x Django 5.2, 6.0
    uvx --with tox-uv tox -e py312-dj60  # a single combination
    uvx --with tox-uv tox -e mypy        # type check

    uv run --python 3.14 pytest          # quick single run, without tox
