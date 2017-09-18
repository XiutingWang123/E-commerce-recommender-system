from sets import Set


def test_model(true_map, predict_map):
    """
    Compute the accuracy of predict items
    :param true_map: a dictionary with user_id and its corresponding recommend items
    :param predict_map: a dictionary with user_id and its corresponding recommend items
    :return: a float, accuracy for training result, accuracy for recent brouwse items
    """

    precision_list = []
    recall_list = []

    for user, items in true_map.iteritems():
        true_set = Set(items)
        predict = predict_map.get(user)
        precision, recall = precision_recall(true_set, predict)
        precision_list.append(precision)
        recall_list.append(recall)

    average_precision = sum(precision_list) / float(len(precision_list))
    average_recall = sum(recall_list) / float(len(recall_list))

    return average_precision, average_recall


def jaccard(ground_truth, predict):
    """
    Jaccard distance: J(X,Y) = |X and Y| / |X or Y|
    :param ground_truth: a set of items
    :param predict: a list of items
    :return: a float, accuracy
    """
    cross = 0
    for item in predict:
        if item in ground_truth:
            cross += 1

    return float(cross) / float(len(ground_truth) + len(predict) - cross)


def precision_recall(ground_truth, predict):
    """
    Compute precision and recall
    Precision = #recommended items that users clicked(purchased) / #recommedned items
    Recall = #recommended items that users clicked(purchased) / #clicked(purchased) items
    :param ground_truth: a set of items
    :param predict: a list of items
    :return: two float, precision and recall
    """
    cross = 0
    for item in predict:
        if item in ground_truth:
            cross += 1

    precision = 0
    if cross == 0 or len(predict) == 0:
        precision == 0
    else:
        precision = cross / float(len(predict))

    recall = 0
    if cross == 0 or len(ground_truth) == 0:
        recall == 0
    else:
        recall = cross / float(len(ground_truth))
    return precision, recall

