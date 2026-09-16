from __future__ import annotations

import requests


OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def query_overpass(query: str) -> dict:
    response = requests.post(
        OVERPASS_URL,
        data=query.encode("utf-8"),
        headers={
            "Content-Type": "text/plain; charset=utf-8",
            "User-Agent": "SatQuery/0.1",
        },
        timeout=300,
    )

    response.raise_for_status()

    return response.json()