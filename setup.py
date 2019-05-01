from setuptools import setup

setup(name='django-rest-framework-mango',
      version='0.1',
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
      packages=['django-rest-framework-mango'],
      long_description=open('README.md').read(),
      install_requires=[
          'django',
          'djangorestframework', ]
      )
