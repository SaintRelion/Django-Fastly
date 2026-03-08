import threading

_thread_locals = threading.local()

def set_current_user(user):
    _thread_locals.user = user

def get_current_user():
    return getattr(_thread_locals, "user", None)

def set_current_ip(ip):
    _thread_locals.ip = ip

def get_client_ip():
    return getattr(_thread_locals, "ip", None)


class CurrentUserMiddleware:
    """Store request user and IP in thread-local storage"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_user(getattr(request, "user", None))
        set_current_ip(request.META.get("REMOTE_ADDR"))
        response = self.get_response(request)
        return response