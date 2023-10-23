from urllib.parse import urljoin

import requests
from flask import current_app

from app.models.tracking import Tracking


def create_tracking(data: Tracking):
    return _session().post(_url('track'), json=data.to_parcellab_input_dict()).json()


def _url(endpoint: str) -> str:
    return urljoin(current_app.config["PARCELLAB_URL"], endpoint)


def _session():
    session = requests.Session()
    headers = {
        "Authorization": "Ariane",
        "X-API-KEY": current_app.config["PARCELLAB_API_KEY"],
    }
    session.headers.update(headers)
    return session
