from abc import ABCMeta, abstractmethod


class BaseRecommendAlgorithm(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def learn(self, train_1, train_2):
        """Create a recommender model based on train_data """
        pass

    @abstractmethod
    def load_model(self, k):
        """Load training model"""
        pass

    @abstractmethod
    def recommend_items(self, model_data, user_id, source_items_map, k):
        """Produce recommendation list with k items"""
        pass
