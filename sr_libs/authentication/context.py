from contextvars import ContextVar

_current_user: ContextVar = ContextVar("_current_user", default=None)
_current_ip: ContextVar = ContextVar("_current_ip", default=None)
_current_system: ContextVar = ContextVar("_current_system", default=None)


def set_current_user(user):
    _current_user.set(user)


def get_current_user():
    return _current_user.get()


def set_current_ip(ip):
    _current_ip.set(ip)


def get_current_ip():
    return _current_ip.get()


def set_current_system(identity_name: str):
    """Call this for system / automated actions."""
    _current_system.set(identity_name)


def get_current_system():
    return _current_system.get()
