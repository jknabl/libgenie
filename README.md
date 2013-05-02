LIBGENIE
--------

Pull books from a (public) AMZN wishlist and see if they're available at a university library.

The genie grabs an ISBN for each book in a given wishlist, then grabs all alternate ISBNs using the LibraryThing API. Genie then searches a chosen library by ISBN, does some scraping and parsing, and pops back a list of available books (library location, checkout status, and call number). 

DEPENDENCIES
------------

See requirements.txt.

Easiest way to get up and running would be to spin up a new venv, then:

pip install -r requirements.txt

RUN
---

python wishlist.py

TODO
----

* Functional but too slow for production. Parallelize HTTP requests.
* Make things pretty.
