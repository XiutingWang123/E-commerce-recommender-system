from abc import ABCMeta, abstractmethod


class BaseRecommendAlgorithm(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def learn(self, train_clicks, train_buys):
        """Create a recommender model based on train_data """
        pass

    @abstractmethod
    def load_model(self, neighborhood_size):
        """Load training model"""
        pass

    @abstractmethod
    def recommend_items(self, model_data, user_id, source_items_map, num_recommended_items):
        """Produce recommendation list with k items"""
        pass
