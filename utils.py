import csv
import itertools
import heapq
import pandas as pd
from sets import Set


def load_data(trainSet_clicks, trainSet_buys, testSet):
    """
    Load data sets in a dataframe format
    :param trainSet_clicks: train data set with clicks record
    :param trainSet_buys: train data set with purchase record
    :param testSet: test data set with clicks record
    :return: dataframes of clicks, buys, and test
    """
    clicks = pd.read_csv(trainSet_clicks, header=None,
                         names=['Session ID', 'Timestamp', 'Item ID', 'Category'])
    buys = pd.read_csv(trainSet_buys, header=None,
                       names=['Session ID', 'Timestamp', 'Item ID', 'Price', 'Quantity'])
    test = pd.read_csv(testSet, header=None,
                       names=['Session ID', 'Timestamp', 'Item ID', 'Category'])
    return clicks, buys, test


def parse_test(test):
    """Group test dataframe by Session ID"""
    test['count'] = test.groupby('Session ID')['Session ID'].transform('count')
    test_count = test[['Session ID', 'Item ID', 'Category', 'count']]

    return test_count


def write_df_output(df, filename):
    """Write dataframe into csv file"""
    root = 'output'
    df.to_csv(root + '/' + filename, sep=',', index=False)


def write_list_output(list_dc, filename):
    """Write a list of dict into csv file"""
    root = 'output'
    keys = list_dc[0].keys()
    with open(root + '/' + filename, 'wb') as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(list_dc)


def split_test(test_count):
    """
    Split test dataframe into source items and test items
    :param test_count: a dataframe
    :return: two dictionaries, the key is user id (session id), value is a list of source items or test items
    """
    """
    test_group = test_count.groupby('Session ID')
    session_map = {}

    for x in test_group.groups:
        df = test_group.get_group(x)
        df_split = np.array_split(df, 2)
        # df_split[0] as source items and df_split[1] as test items
        for row in df_split[1].itertuples():
            if row[1] not in session_map:
                session_map[row[1]] = Set()
            session_map[row[1]].add(row[-2])
    """

    source_items_map = {}
    test_items_map = {}

    for row in test_count.itertuples():
        if row[1] not in source_items_map:
            source_items_map[row[1]] = []
        source_items_map[row[1]].append(row[2])

    for key, value in source_items_map.iteritems():
        half = len(value) / 2
        test_items_map[key] = [None] * half
        for i in range(half):
            test_items_map[key][i] = value.pop()

    return source_items_map, test_items_map


def create_inverted_index(df, idx1, idx2):
    """
    Create an inverted index with df[row][idx1] as key, df[row][idx2] as value
    :param df: a dataframe
    :param idx1: the index in each row of dataframe that represent key
    :param idx2: the index in each row of dataframe that represent value
    :return: a dict with session Id as key and item id as value
    """
    inverted_index_map = {}
    for row in df.itertuples():
        if row[idx1] not in inverted_index_map:
            inverted_index_map[row[idx1]] = Set()
        inverted_index_map[row[idx1]].add(row[idx2])

    return inverted_index_map


def compute_items_sim(inverted_index, items_list):
    """
    Compute the similarity between each item from inverted index
    :param inverted_index: a dict with session Id as key and item id as value
    :param items_list: a list containing all items
    :return: a list of dicts, each dict store the relevant score between item i and item j
    """

    item_count = {}
    item_pair_count = {}
    item_num_threshold = len(items_list) * 0.8

    for session, items in inverted_index.iteritems():
        if len(items) == 0 or len(items) > item_num_threshold:
            continue
        # count items
        for item in items:
            if item in item_count:
                item_count[item] = item_count[item] + 1
            else:
                item_count[item] = 1
        # count item pair
        for first_item, second_item in itertools.combinations(items, 2):
            key = str(first_item) + '_' + str(second_item)
            if first_item > second_item:
                key = str(second_item) + '_' + str(first_item)
            if key in item_pair_count:
                item_pair_count[key] = item_pair_count[key] + 1
            else:
                item_pair_count[key] = 1

    # count sim for each item pair and put in a list of dict
    items_sim_list = get_sim_list(item_count, item_pair_count)

    return items_sim_list


def get_sim_list(item_count, item_pair_count):
    """
    Get the a list of dicts that contain the similarity of all item pairs
    :param item_count: a dict with key is each item, and the orresponding value is its occurrence
    :param item_pair_count: a dict with key is item1_item2, and its value is the similarity between the two items
    :return: a list of dicts, each dict contains item1, item2 and similarity
    """
    sim_list = [None] * len(item_pair_count)
    i = 0
    for key, val in item_pair_count.iteritems():
        key_split = key.split('_')
        len_first = item_count.get(int(key_split[0]))
        len_second = item_count.get(int(key_split[1]))
        sim = val / float(len_first + len_second - val)
        sim_map = {'Item 1': int(key_split[0]), 'Item 2': int(key_split[1]), 'Similarity': sim}
        sim_list[i] = sim_map
        i += 1

    return sim_list


def get_item_neighbor(clicks_sim, neighborhood_size):
    """
    Create a dict with each item and its neighbors
    :param clicks_sim: a dataframe contains each item pairs and their similarity
    :param neighborhood_size: an integer
    :return: a dict with each item as a key and a list of tuple(similarity, neighbor) as value
    """

    item_neighbor = {}
    for row in clicks_sim.itertuples():
        if row[1] not in item_neighbor:
            heap = []
            heapq.heapify(heap)
            item_neighbor[row[1]] = heap
        if row[2] not in item_neighbor:
            heap = []
            heapq.heapify(heap)
            item_neighbor[row[2]] = heap
        # push a tuple(similarity, neighbor) into heap, only maintain top k
        heapq.heappush(item_neighbor[row[1]], (row[-1], row[2]))
        if len(item_neighbor[row[1]]) > neighborhood_size:
            heapq.heappop(item_neighbor[row[1]])

        heapq.heappush(item_neighbor[row[2]], (row[-1], row[1]))
        if len(item_neighbor[row[2]]) > neighborhood_size:
            heapq.heappop(item_neighbor[row[2]])

    print 'item_neighbor dict is built'
    return item_neighbor


def get_rec_list(item_neighbor, source_items, k):
    """
    Get k recommend items based on the source_items
    :param item_neighbor: a dist with each item as a key and a list of tuple(similarity, neighbor) as value
    :param source_items: a list of items that a user recently clicks
    :param k: an integer, representing k items that will be recommended
    :return: a list of k recommend items
    """
    recommend = {}
    source_set = Set(source_items)
    i = 0
    for item in source_set:
        if item not in item_neighbor:
            continue
        i += 1
        for nei in item_neighbor.get(item):
            if nei[1] in source_set:
                continue
            if nei[1] in recommend:
                recommend[nei[1]] = recommend[nei[1]] + nei[0]
            else:
                recommend[nei[1]] = nei[0]
        # only use part of source items to make recommendation
        if i >= 3 and len(recommend) >= k:
            break

    sorted_recommend = heapq.nlargest(k, recommend, key=recommend.get)

    return sorted_recommend


def get_lowprice(df, price_threshold):
    """
    :param df: a dataframe
    :param price_threshold: an integer, representing the min price
    :return: a set that contains Item ID with price < price_threshold
    """
    s = Set()
    for row in df.itertuples():
        if row[-3] < price_threshold:
            s.add(row[-4])
    return s
