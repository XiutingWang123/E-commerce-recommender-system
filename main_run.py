import sys
import utils
import time
from model import Popularity, ItemkNN
from evaluation import test_model


USAGE = "<trainset_clicks> <trainset_buys> <testset> <model> <num_recommended_items>"
USAGE_HINT = "model should be a string, num_recommended_items should be an integer."
price_threshold = 50
neighborhood_size = 6
MODELS = {'popularity': Popularity(),
          'itemknn': ItemkNN()}


def getArgs():
    if len(sys.argv) < 6:
        print >> sys.stderr, "Usage: {0} {1}".format(sys.argv[0], USAGE)
        exit(-1)

    try:
        return sys.argv[1], sys.argv[2], sys.argv[3], str(sys.argv[4]), int(sys.argv[5])
    except ValueError:
        print >> sys.stderr, "Usage: {0} {1} ({2})".format(sys.argv[0], USAGE, USAGE_HINT)
        exit(-1)


if __name__ == '__main__':
    trainSet_clicks, trainSet_buys, testSet, model, num_recommended_items = getArgs()
    clicks, buys, test = utils.load_data(trainSet_clicks, trainSet_buys, testSet)
    test_count = utils.parse_test(test)
    user_id = test_count['Session ID']
    source_items_map, test_items_map = utils.split_test(test_count)

    mod = MODELS.get(model)

    start_time = time.time()
    mod.learn(clicks, buys, price_threshold)
    print 'Training time: %s seconds' % (time.time() - start_time)
    
    model_data = mod.load_model(neighborhood_size)
    recommend_time = time.time()
    user_recommend_map = mod.recommend_items(model_data, user_id, source_items_map, num_recommended_items)
    print 'Average throughput: {} users per second'.\
        format(len(user_recommend_map) / (time.time() - recommend_time))
    precision, recall = test_model(user_recommend_map, test_items_map)

    print 'Precision for clicks items: {}'.format(precision)
    print 'Recall for clicks items: {}'.format(recall)
    




