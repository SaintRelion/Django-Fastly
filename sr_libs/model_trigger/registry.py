import threading
from typing import List, Optional

from sr_libs.model_trigger.models import ReactiveRule, ScheduledRule


class ModelTriggerRegistry:
    def __init__(self):
        self._registry = {}
        self._lock = threading.Lock()

    def register(
        self,
        model,
        reactive_rules: Optional[List[ReactiveRule]] = None,
        scheduled_rules: Optional[List[ScheduledRule]] = None,
    ):
        model_label = f"{model._meta.app_label}.{model.__name__}"
        with self._lock:
            self._registry[model_label] = {
                "model": model,
                "reactive_rules": reactive_rules or [],
                "scheduled_rules": scheduled_rules or [],
            }

    def get(self, model_label):
        return self._registry.get(model_label)

    def all(self):
        return self._registry.values()


# global singleton
registry = ModelTriggerRegistry()
