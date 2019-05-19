import threading


class SessionMiddleware:
    _sessions = {}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self._init_session()

        response = self.get_response(request)

        self._remove_session()

        return response

    def _init_session(self):
        self._sessions[threading.current_thread()] = {}

    def _remove_session(self):
        self._sessions.pop(threading.current_thread(), None)

    @classmethod
    def get_session(cls):
        return cls._sessions.get(threading.current_thread())
