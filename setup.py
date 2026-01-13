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
    version='0.1.9',
    description='Python package to download phenological data from Wekeo (HR-VPP datasets from Sentinel 2)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Diego García Díaz',
    author_email='digd.geografo@gmail.com',
    maintainer='Diego García Díaz',
    maintainer_email='digd.geografo@gmail.com',
    url='https://github.com/Digdgeo/PyVPP',
    license='MIT',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        'hda>=2.18',
        'deims>=4.0',
        'geopandas>=0.8.2',
        'pyproj>=3.0',
        'rasterio>=1.3',
        'requests>=2.20',
        'fiona>=1.8.20',
        'shapely>=1.8'
    ],
    extras_require={
        'dev': [
            'pytest>=7.2.1',
            'black>=23.1.0'
        ]
    },
    keywords=['phenology', 'hrvpp', 'vegetation indexes', 'copernicus', 'wekeo'],
    classifiers=[
        'Development Status :: 4 - Beta',
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
