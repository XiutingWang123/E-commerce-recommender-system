from bottle import route, run, template, post, request
from model import ItemkNN

k = 5

@route('/recommend')
def index():
    # try 214507408 214507492
    return '''<form action="/recommend" method="post">\
    Enter source item ID: <input name="keywords" type="text" /><input type="submit" /></form>'''


@route('/recommend', method='POST')
def show_recommend():
    # get data from user's post
    # which is a list of item ids in String format
    source_items = request.forms.get('keywords').split()
    recommend_list = run_recommend_engine(source_items, k)
    output = template('show_recommend_items', recommend_list=recommend_list, keyword=source_items)
    return output


def run_recommend_engine(source_items, k):
    """
    Run recommend engine to make recommendation
    :param source_items: a list of item id (String)
    :param k: an integer
    :return: a list of recommend items
    """
    mod = ItemkNN()
    model_data = mod.load_model(k)
    # make a pseudo user_id
    user_id = [1]
    source_items_map = {user_id[0]: map(int, source_items)}
    user_recommend_map = mod.recommend_items(model_data, user_id, source_items_map, k)
    return user_recommend_map.get(user_id[0])


if __name__ == '__main__':
    run(host='localhost', port=8080, reloader=True)


