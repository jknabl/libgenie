from flask import Flask
import flask
import pprint
import models
import os
app = Flask(__name__)

@app.route('/')
def models_index():
    return flask.render_template('index.html')


# Results page
@app.route('/search', methods=['GET'])
def do_search():
    #data = flask.request.form['library']
    #email = flask.request.form['email']
    data = flask.request.args['library']
    email = flask.request.args['email']
    the_wishlist = models.Wishlist(email)
    print the_wishlist
    search_result = search(data, the_wishlist)
    return flask.render_template('result.html', result=search_result)

def search(library, the_wishlist):
    search_results = []
    if library=='carleton':
        print "In carleton search"
        search_obj = models.CarletonSearch(the_wishlist)
        search_results = search_obj.search_all()
    if library=='uottawa':
        search_obj = models.OttawaUSearch(the_wishlist)
        search_results = search_obj.search_all()
    if library=='western':
       search_obj = models.WesternSearch(the_wishlist)
       search_results = search_obj.search_all()
    if library=='brock':
        search_obj = models.OttawaUSearch(the_wishlist)
        search_results = search_obj.search_all()
    if library=='windsor':
        search_obj = models.OttawaUSearch(the_wishlist)
        search_results = search_obj.search_all()
    if library=='queens':
        search_obj = models.QueensSearch(the_wishlist)
        search_results = search_obj.search_all()
    if library=='york':
        search_obj = models.YorkSearch(the_wishlist)
        search_results = search_obj.search_all()
    if library=='lakehead':
        search_obj = models.LakeheadSearch(the_wishlist)
        search_results = search_obj.search_all()
    if library=='ryerson':
        search_obj = models.RyersonSearch(the_wishlist)
        search_results = search_obj.search_all()
    if library=='ocad':
        search_obj = models.OCADSearch(the_wishlist)
        search_results = search_obj.search_all()
    return search_results

if __name__=='__main__':
    #app.debug = True
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host="0.0.0.0", port=port)
