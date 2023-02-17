import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

classifiers = [
	'Intended Audience :: eLTER PIs and any researcher interested in Phenology',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Operating System :: OS Independent'
]


setup(
	name='pyvpp',
	version='0.0.1',
	description='Python package to download phenological data (HR-VPP products) from Wekeo.',
	long_description=read('README.md'),
	url='https://github.com/Digdgeo/PyVPP',
	python_requires='>=3.5',
	author='Diego Garcia Diaz',
	author_email='digd.geografo@gmail.com',
	license='MIT',
	install_requires=['deims, hda'],
	packages=find_packages(include=['pyvpp', 'pyvpp.*']),
	zip_safe=False