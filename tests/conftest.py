import django
from django.conf import settings

settings.configure(
    SECRET_KEY='test',
    USE_TZ=True,
    DATABASES={},
    INSTALLED_APPS=['django.contrib.contenttypes', 'django.contrib.auth', 'rest_framework'],
)
django.setup()
