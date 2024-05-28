from abc import ABC, abstractmethod


class BasePriceProvider(ABC):
    @abstractmethod
    def process_prices(self):
        """
        Abstract method to process prices.
        :param prices: A dictionary of prices.
        :return: Processed prices.
        """
        pass
