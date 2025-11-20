from abc import ABC, abstractmethod
from typing import Dict, Any

import pandas as pd


class Strategy(ABC):
    """
    Base class for strategies. This class provides a simple interface/framework
    for how a strategy is built.
    """

    def __init__(self, name="strategy"):
        self.name = name

    @abstractmethod
    def on_start(self):
        """
        Method that houses logic for data fetching, pre-processing, pre-market
        calculations, model training/initialization etc.
        """
        pass

    @abstractmethod
    def on_data(self, data: Dict | pd.DataFrame):
        """
        Method that houses logic for evaluating data that comes in, executing
        trades, managing positions, etc.
        :param data: Input data (bar, tick, other.)
        """
        pass

    @abstractmethod
    def on_stop(self):
        """
        Method that houses logic for cleaning up connections, closing positions,
        post-processing, saving data, etc.
        """
        pass

    @abstractmethod
    def run(self):
        """
        Method that houses logic for calling on_start(), on_data() and on_stop()
        and any other "glue" logic.

        Example:
            try:
                self.on_start()
                for data in data_stream:  # glue logic
                    should_trade = self.on_data(data)
                    if should_trade:
                        execute_trade()
            except Exception:
                raise
            finally:
                self.on_stop()
        """
        pass
