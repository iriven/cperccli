#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
__pkgname__ = 'python3-cperccli'
__pkgalias__ = 'cperccli'
__intname__ = __pkgname__.lower() + '.setup'
__author__ = 'Alfred TCHONDJO'
__email__ = 'iriven@yahoo.fr'
__copyright__ = 'Copyright (C) 2021-2023 IRIVEN France'
__licence__ = 'MIT License' 
__build__ = '2023052810'
__version__ = '1.0.1'

import os
import sys
from pathlib import Path
from setuptools import find_packages, setup

if sys.version_info < (3, 6):
    sys.exit('Python 3.6 is the minimum required version')

README = 'README.md'
CWD = Path(__file__).parent
DESC = (CWD / README).read_text()
AUTORUN_PATH='/usr/local/bin'

setup(
    name=__pkgname__,
    version=__version__,
    url='https://github.com/iriven/' + __pkgalias__.lower(),
    author=__author__,
    author_email=__email__,
    long_description=f'\n{DESC}',
    long_description_content_type='text/markdown',
    license=__licence__,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    python_requires='>=3.6',
    keywords='cperccli wrapper PERC Dell',
    classifiers=[
        'Development Status :: 3 - stable',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
    ],
)
