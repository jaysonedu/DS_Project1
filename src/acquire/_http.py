"""HTTP helpers with retries and timeouts."""

from __future__ import annotations

import time

import requests

from ._utils import DEFAULT_RETRIES, DEFAULT_RETRY_BACKOFF, DEFAULT_TIMEOUT


def get_with_retries(
    url: str,
    *,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: int = DEFAULT_TIMEOUT,
    max_retries: int = DEFAULT_RETRIES,
    backoff: float = DEFAULT_RETRY_BACKOFF,
) -> requests.Response:
    """GET with retries and exponential backoff. Raises on final failure."""
    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            r = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout,
            )
            r.raise_for_status()
            return r
        except (requests.RequestException, requests.ConnectionError) as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(backoff**attempt)
    msg = f"Failed after {max_retries} attempts: {last_error}"
    raise RuntimeError(msg) from last_error
