import pandas as pd
from sets import Set
import utils
from base_recommend_algorithm import BaseRecommendAlgorithm


ITEM_ID = 'Item ID'
ITEM_PRICE = 'Price'
QUANTITY = 'Quantity'
POPULARITY = 'Popularity'


class Popularity(BaseRecommendAlgorithm):
    def __init__(self):
        self.clicks = None
        self.buys = None
        self.user_id = None
        self.clicks_pop = None
        self.buys_pop = None

    def learn(self, clicks, buys, price_threshold):
        """
        Create a popularity based recommender system model
        :param clicks: a dataframe with clicks record
        :param buys: a dataframe with buys record
        :param price_threshold: the minimum price that
        """
        self.clicks = clicks
        self.buys = buys

        # create a new dataframe sorted by clicks frequency
        clicks[POPULARITY] = clicks.groupby(ITEM_ID)[ITEM_ID].transform('count')
        clicks_pop = clicks[[ITEM_ID, POPULARITY]].drop_duplicates(subset=ITEM_ID, keep='first')
        # clicks_pop = clicks_pop[~clicks_pop['Item ID'].isin(lowprice_set)]
        clicks_pop = clicks_pop.sort_values(POPULARITY, ascending=False)
        self.clicks_pop = clicks_pop

        # create a new dataframe sorted by purchase frequency
        buys[POPULARITY] = buys.groupby(ITEM_ID)[ITEM_ID].transform('count')
        buys_pop = buys[[ITEM_ID, ITEM_PRICE, QUANTITY, POPULARITY]]
        buys_pop = buys_pop.drop_duplicates(subset=ITEM_ID, keep='first')
        #lowprice_set = utils.get_lowprice(buys_freq, self.price_threshold)
        buys_pop = buys_pop[buys_pop[ITEM_PRICE] > price_threshold]
        buys_pop[POPULARITY] = buys_pop[POPULARITY] * buys_pop[QUANTITY]
        buys_pop = buys_pop.sort_values(POPULARITY, ascending=False)
        buys_pop = buys_pop[[ITEM_ID, POPULARITY]]
        self.buys_pop = buys_pop

        # write train model to csv files
        utils.write_df_output(clicks_pop, 'clicks_pop_model.csv')
        utils.write_df_output(buys_pop, 'buys_pop_model.csv')

        print 'Popularity model for both clicks and buys are built'

    def load_model(self, k):
        """
        Load training model
        :param k: an integer, not be used here
        :return: a dataframe of recommender model based on item popularity
        """
        clicks_pop = pd.read_csv('output/clicks_pop_model.csv')
        return clicks_pop

    def recommend_items(self, clicks_pop, user_id, source_items_map, k):
        """
        Use the popularity based recommender system model to make recommendations
        :param clicks_pop: a dataframe of recommender model based on item popularity
        :param user_id: a series of user_id
        :param source_items_map: not be used here
        :param k: an integer, representing k items that will be recommended
        :return: a dictionary with user_id and its corresponding recommend items
        """
        self.user_id = Set(user_id)
        recommend = []

        i = 0
        for item in clicks_pop.itertuples():
            recommend.append(item[1])
            i += 1
            if i == k:
                break

        user_recommend_map = {}
        for id in self.user_id:
            if id not in user_recommend_map:
                user_recommend_map[id] = recommend

        return user_recommend_map


class ItemkNN(BaseRecommendAlgorithm):
    def __init__(self):
        self.clicks = None
        self.buys = None
        self.user_id = None
        self.clicks_sim_list = None
        self.buys_sim_list = None

    def learn(self, clicks, buys, price_threshold):
        """
        Create an item kNN based recommender system model
        :param clicks: a dataframe with clicks record
        :param buys: a dataframe with buys record
        :param price_threshold: the minimum price that
        :return: a recommender model based on item similarity
        """
        self.clicks = clicks
        self.buys = buys

        # extract all item id from clicks
        items_list_clicks = clicks[ITEM_ID].drop_duplicates().sort_values().reset_index(drop=True)
        # create an inverted index for each Session id based on clicks record
        inverted_index_clicks = utils.create_inverted_index(clicks, 1, 3)
        # compute the similarity between each item
        clicks_sim_list = utils.compute_items_sim(inverted_index_clicks, items_list_clicks)
        self.clicks_sim_list = clicks_sim_list


        # extract all item id from buys
        items_list_buys = buys[ITEM_ID].drop_duplicates().sort_values().reset_index(drop=True)
        # create an inverted index for each Session id based on purchase record
        inverted_index_buys = utils.create_inverted_index(buys, 1, 3)
        # compute the similarity between each item
        buys_sim_list = utils.compute_items_sim(inverted_index_buys, items_list_buys)
        self.buys_sim_list = buys_sim_list

        # write train model to csv files
        utils.write_list_output(clicks_sim_list, 'clicks_itemknn_model.csv')
        utils.write_list_output(buys_sim_list, 'buys_itemknn_model.csv')

        print 'Item kNN model for both clicks and buys are built'

    def load_model(self, k):
        """
        Load training model
        :param k: an integer
        :return: a dict with each item as a key and a list of tuple(similarity, neighbor) as value
        """
        clicks_sim = pd.read_csv('output/clicks_itemknn_model.csv')
        item_neighbor = utils.get_item_neighbor(clicks_sim, k)
        return item_neighbor

    def recommend_items(self, item_neighbor, user_id, source_items_map, k):
        """
        Use the item kNN based recommender system model to make recommendations
        :param item_neighbor: a dict with each item as a key and a list of tuple(neighbors, similarity) as value
        :param user_id: a series of user_id
        :param source_items_map: a dict with key is user and value is a list of user's recent clicks items
        :param k: an integer
        :return: a dictionary with user_id and its corresponding recommend items
        """
        self.user_id = Set(user_id)

        user_recommend_map = {}
        for id in self.user_id:
            recommend = utils.get_rec_list(item_neighbor, source_items_map.get(id), k)
            user_recommend_map[id] = recommend
            #print 'finish {0}/{1} user recommend list'.format(id, len(user_id))

        print 'All user recommend lists are built'
        return user_recommend_map


