"""
PyVPP - Python library for downloading and processing vegetation products.

Supports both:
- HR-VPP products from Copernicus via WEkEO (pyvpp.wekeo)
- Sentinel-2 L2A raw data via CDSE (pyvpp.cdse)
"""

__version__ = '1.0.0'

# Import from wekeo submodule
from pyvpp.wekeo import (
    wekeo_download,
    create_hdarc,
    delete_hdarc,
    clean_old_hdarc,
    get_utm_zones,
)

# Import from cdse submodule
from pyvpp.cdse import (
    CDSEDownload,
    load_cdse_credentials,
)

# Export all public functions
__all__ = [
    # WEkEO functions
    'wekeo_download',
    'create_hdarc',
    'delete_hdarc',
    'clean_old_hdarc',
    'get_utm_zones',
    # CDSE functions
    'CDSEDownload',
    'load_cdse_credentials',
]
