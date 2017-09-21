from bottle import route, run, template, post, request
from model import Popularity, ItemkNN

neighborhood_size = 3
num_recommended_items = 3

@route('/recommend')
def index():
    # try 214507408 214507492, 1178794852 643078950
    return '''<form action="/recommend" method="post">\
    Enter source item ID: <input name="keywords" type="text" /><input type="submit" /></form>'''


@route('/recommend', method='POST')
def show_recommend():
    # get data from user's post
    # which is a list of item ids in String format
    source_items = request.forms.get('keywords').split()
    recommend_list = run_recommend_engine(source_items)
    output = template('show_recommend_items', recommend_list=recommend_list, keyword=source_items)
    return output


def run_recommend_engine(source_items):
    """
    Run recommend engine to make recommendation
    :param source_items: a list of item id (String)
    :return: a list of recommend items from both popularity model and popularity model
    """
    # make a pseudo user_id
    user_id = [1]
    source_items_map = {user_id[0]: map(int, source_items)}

    mod1 = Popularity()
    mod1_data = mod1.load_model(neighborhood_size)
    user_recommend_map_1 = mod1.recommend_items(mod1_data, user_id, source_items_map, num_recommended_items)

    mod2 = ItemkNN()
    mod2_data = mod2.load_model(neighborhood_size)
    user_recommend_map_2 = mod2.recommend_items(mod2_data, user_id, source_items_map, num_recommended_items)
    return [user_recommend_map_1.get(user_id[0]), user_recommend_map_2.get(user_id[0])]


if __name__ == '__main__':
    run(host='localhost', port=8080, reloader=True)


