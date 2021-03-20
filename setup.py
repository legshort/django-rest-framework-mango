from setuptools import setup

setup(name='djangorestframework_mango',
      version='0.2.0',
      url='https://github.com/legshort/django-rest-framework-mango/',
      license='MIT',
      author='Jun Young Lee',
      author_email='legshort@gmail.com',
      description='A set of viewset mixin for the Django REST Framework.',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
      ],
      keywords=['djangorestframework', 'drf', 'util', 'viewset'],
      packages=['django_rest_framework_mango'],
      long_description=open('README.rst').read(),
      install_requires=[
          'django',
          'djangorestframework',]
      )
