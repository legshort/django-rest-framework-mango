import threading

import pytest

from django_rest_framework_mango.middlewares import SessionMiddleware


def test_session_available_during_request():
    seen = {}

    def view(request):
        seen['session'] = SessionMiddleware.get_session()
        return 'response'

    assert SessionMiddleware(view)(None) == 'response'
    assert seen['session'] == {}


def test_session_cleared_after_request():
    SessionMiddleware(lambda request: None)(None)

    assert SessionMiddleware.get_session() is None


def test_session_cleared_when_view_raises():
    def view(request):
        raise ValueError('boom')

    with pytest.raises(ValueError):
        SessionMiddleware(view)(None)

    assert SessionMiddleware.get_session() is None


def test_session_is_isolated_per_thread():
    def view(request):
        SessionMiddleware.get_session()['owner'] = threading.current_thread().name
        other = []
        thread = threading.Thread(target=lambda: other.append(SessionMiddleware.get_session()))
        thread.start()
        thread.join()
        return other[0]

    assert SessionMiddleware(view)(None) is None
