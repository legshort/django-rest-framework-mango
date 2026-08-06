from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Any, Callable, ClassVar

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponseBase


class SessionMiddleware:
    # ponytail: threading.local() is exactly this feature, no dict keyed by Thread to reap.
    _local: ClassVar[threading.local] = threading.local()

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponseBase]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        self._local.session = {}

        try:
            return self.get_response(request)
        finally:
            self._local.session = None

    @classmethod
    def get_session(cls) -> dict[str, Any] | None:
        return getattr(cls._local, 'session', None)
