from abc import ABC, abstractmethod


class Recommender(ABC):
    """Base class for a recommendation system.
    """
    def __init__(self):
        pass

    @abstractmethod
    def predict_for_movie(self, *args, **kwargs):
        pass

    @abstractmethod
    def predict_for_user(self, *args, **kwargs):
        pass
