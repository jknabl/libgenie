LIBGENIE

Pull books from a (public) AMZN wishlist and see if they're available at a university library.

The genie grabs an ISBN for each book in a given wishlist, then grabs alternate ISBNs using the LibraryThing API. Genie searches a chosen library by ISBN, does some scraping and parsing, and pops back a list of available books (library location, checkout status, and call number). 

TODO

* Functional but too slow for production. Parallelize HTTP requests.
