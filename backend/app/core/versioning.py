from datetime import datetime
from typing import Optional
from fastapi import Response


def set_deprecation_headers(
    response: Response,
    sunset: Optional[str] = None,
    guide_link: Optional[str] = None,
) -> None:
    """
    Mark an endpoint response as deprecated using standard headers.

    - Deprecation: true
    - Sunset: <RFC 1123 date> (optional)
    - Link: <https://.../migration-guide>; rel="deprecation" (optional)
    """
    response.headers["Deprecation"] = "true"
    if sunset:
        response.headers["Sunset"] = sunset
    if guide_link:
        response.headers["Link"] = f'<{guide_link}>; rel="deprecation"'


