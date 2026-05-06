"""
Copernicus Data Space Ecosystem (CDSE) module for Sentinel-2 data.
"""

from pyvpp.cdse.cdse import CDSEDownload
from pyvpp.cdse.config import load_cdse_credentials

__all__ = [
    'CDSEDownload',
    'load_cdse_credentials',
]
