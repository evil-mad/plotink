"""
Based on https://github.com/pypa/sampleproject

"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='plotink',
    version='1.0.0',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/evil-mad/plotink',
    author='Evil Mad Scientist Laboratories',
    author_email='contact@evilmadscientist.com',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'ink_extensions'
    ],
    extras_require={
        'dev': [],
        'test': [],
    },
)
