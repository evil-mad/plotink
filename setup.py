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
    version='1.2.0',
    python_requires='>=3.5.0',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/evil-mad/plotink',
    author='Evil Mad Scientist Laboratories',
    author_email='contact@evilmadscientist.com',
    description="Helper routines for use with plotters",
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "Intended Audience :: Developers",
    ],

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'ink_extensions',
        'pyserial==3.5b0',
    ],
    extras_require={
        'dev': ['coverage'],
        'test': [],
    },
)
