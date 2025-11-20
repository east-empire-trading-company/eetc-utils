from typing import Dict, Any


class Strategy:
    """
    Base class for strategies.
    """

    def __init__(self, name="strategy"):
        self.name = name

    def on_start(self, context: Dict[str, Any]):
        pass

    def on_data(self, data: Dict[str, Any], timestamp, context: Dict[str, Any]):
        raise NotImplementedError

    def on_stop(self, context: Dict[str, Any]):
        pass
