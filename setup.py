import re

from setuptools import find_packages
from setuptools import setup

# get metadata from mudule using a regexp
with open('legal_advice_builder/__init__.py') as f:
    metadata = dict(re.findall(r'__(.*)__ = [\']([^\']*)[\']', f.read()))

setup(
    name=metadata['title'],
    version=metadata['version'],
    author=metadata['author'],
    author_email=metadata['email'],
    maintainer=metadata['author'],
    maintainer_email=metadata['email'],
    license=metadata['license'],
    url='https://github.com/OpenLegalTech',
    install_requires=[
        'Django',
        'django-treebeard',
        'WeasyPrint',
        'Markdown',
        'bleach',
        'django-tinymce'
    ],
    packages=find_packages(),
    include_package_data=True
)
