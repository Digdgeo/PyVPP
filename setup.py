#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for PyVPP
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='pyvpp',
    version='1.0.0',
    description='Python package to download and process vegetation products from WEkEO (HR-VPP) and CDSE (Sentinel-2)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Diego García Díaz',
    author_email='digd.geografo@gmail.com',
    maintainer='Diego García Díaz',
    maintainer_email='digd.geografo@gmail.com',
    url='https://github.com/Digdgeo/PyVPP',
    license='MIT',
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=[
        'requests>=2.28',
        'geopandas>=0.14',
        'rasterio>=1.3',
        'pyproj>=3.4',
        'shapely>=1.8',
        'deims>=3.1',
        'fiona>=1.8.20',
        'hda>=2.18',
    ],
    extras_require={
        'dev': [
            'pytest>=7.2',
            'black>=23.1'
        ]
    },
    keywords=['phenology', 'hrvpp', 'vegetation indexes', 'copernicus', 'wekeo', 'cdse', 'sentinel-2', 'remote-sensing'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/Digdgeo/PyVPP/issues',
        'Source': 'https://github.com/Digdgeo/PyVPP',
    },
)
