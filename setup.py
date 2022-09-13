#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages
from crossref import __version__

REPO_URL = "https://github.com/GeoLuminate/django-crossref"

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-crossref',
    packages=find_packages(),
    include_package_data=True,
    version=__version__,
    author='Sam Jennings',
    author_email='samuel.scott.jennings@gmail.com',
    license='MIT',
    description='A publication management app with Crossref integration',
    url=REPO_URL,
    install_requires=[
        "Django>=3,<4",    
        "habanero==1.0.0",  
        "django-sortedm2m", 

        ],
    keywords='scientific django publications citations crossref',
    classifiers=[
        'Development Status :: 1 - Development',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'Natural Language :: English',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)