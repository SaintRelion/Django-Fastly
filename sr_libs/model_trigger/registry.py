import threading


class ModelSchedulerRegistry:
    """
    Holds declarative registration of models + triggers/resolvers.
    Supports:
    - reactive triggers (post_save)
    - scheduled/timestamp triggers
    """

    def __init__(self):
        self._registry = {}
        self._lock = threading.Lock()

    def register(
        self,
        model,
        triggers=None,
        resolver=None,
        query_filter=None,
        notification_type="in_app",
        scheduled=None,
    ):
        """
        scheduled: dict with keys:
            - scheduled_at (datetime or callable)
            - repeat_every (timedelta, optional)
            - stop_condition (dict, optional)
            - action (dict, optional)
            - notification_type (optional)
        """
        model_label = f"{model._meta.app_label}.{model.__name__}"
        with self._lock:
            self._registry[model_label] = {
                "model": model,
                "triggers": triggers or {},
                "resolver": resolver,
                "query_filter": query_filter,
                "notification_type": notification_type,
                "scheduled": scheduled,
            }

    def get(self, model_label):
        return self._registry.get(model_label)

    def all(self):
        return self._registry.values()


# global singleton
registry = ModelSchedulerRegistry()


def register_model(
    model,
    triggers=None,
    resolver=None,
    query_filter=None,
    notification_type="in_app",
    scheduled=None,
):
    """Client-facing API for declarative registration."""
    registry.register(
        model=model,
        triggers=triggers,
        resolver=resolver,
        query_filter=query_filter,
        notification_type=notification_type,
        scheduled=scheduled,
    )
