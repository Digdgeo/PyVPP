import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

classifiers = [
	'Intended Audience :: eLTER sites PIs and any researcher interested in phenological satellite data',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Operating System :: OS Independent'
]


setup(
	name='pyvpp',
	version='0.1.1',
	description='Python package to search, download, mosaic and crop sentinel 2 HrVPP products',
	long_description=read('README.md'),
	url='https://github.com/Digdgeo/PyVPP',
	python_requires='>=3.7',
	author='Diego Garcia Diaz',
	author_email='digd.geografo@gmail.com',
	license='MIT',
	install_requires=['hda >= 1.13', 'deims >= 3.1', 'rasterio >= 1.3.6', 'geopandas >= 0.12.2', 'pyproj >= 3.4.1'],
	packages=find_packages(include=['pyvpp', 'pyvpp.*']),
	zip_safe=False
)