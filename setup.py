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
    version='1.9.0',
    python_requires='>=3.6.0',
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

    packages=find_packages(exclude=['contrib', 'docs', 'test', 'test.*']),
    install_requires=[
        'ink_extensions',
        'mpmath>=1.3.0',
        'packaging>=21.0',
        'pyserial>=3.5',
    ],
    extras_require={
        'dev': ['coverage'],
        'test': [],
    },
)
