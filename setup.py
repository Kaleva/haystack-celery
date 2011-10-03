from setuptools import setup, find_packages

setup(
    name='haystack-celery',
    packages=find_packages(),
    include_package_data=True,
    description='Haystack Celery SearchIndex',
    long_description=open('README.md').read(),
    zip_safe=False,
)
