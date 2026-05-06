# pyvpp/cdse/auth.py
import requests
from pyvpp.cdse.config import load_cdse_credentials


def get_cdse_token(user=None, password=None):

    user, password = load_cdse_credentials(user, password)

    url = (
        "https://identity.dataspace.copernicus.eu"
        "/auth/realms/CDSE/protocol/openid-connect/token"
    )

    data = {
        "grant_type": "password",
        "client_id": "cdse-public",
        "username": user,
        "password": password,
    }

    r = requests.post(url, data=data)
    r.raise_for_status()
    return r.json()["access_token"]

