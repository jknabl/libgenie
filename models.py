#!/usr/bin/env python
import httplib
import urllib
import lxml.html
import re
from urlparse import urlparse
from lxml import etree
class Wishlist(object):
    """Class representing an Amazon wishlist.

    """
    def __init__(self, email=""):
        self.email = email
        self.url = self.get_url(email)
        self.books = self.get_books(self.url)
    def get_url(self, email=None):
        #Make HTTP request to amzn to get URL
        #for a user's wishlist
        if email is None:
            email = self.email
        conn = httplib.HTTPConnection("www.amazon.com")
        conn.request("GET", "/registry/search.html?type=wishlist&field-name=%s" % email)
        response = conn.getresponse()
        loc = response.getheader('location')
        return loc
    def get_books(self, url=None):
        the_books = []
        if url is None:
            url = self.url
        url_contents = urllib.urlopen(url).read()
        parsed = lxml.html.document_fromstring(url_contents)
        XMLitems = parsed.find_class("small productTitle")
        for a in parsed.cssselect('span.productTitle a'):
            regex = re.compile("/([\d\w-]+)\/dp\/([\d\w]+)")
            new_url = urlparse(a.get('href'))
            match = regex.match(new_url.path)
            if match:
                new_book = WishlistBook(a.text, new_url.path.rsplit('/')[3], a.get('href'))
                the_books.append(new_book)
        return the_books
    def print_all_books(self):
        for book in self.books:
            book.print_attributes()

class WishlistBook(object):
    def __init__(self, title="", isbn="", url=""):
        self.title = title
        self.isbn = isbn
        self.url = url
        self.alt_isbns = self.get_alt_isbns(isbn)
    def print_attributes(self):
        print "\nBook's title is %s" % self.title
        print "\nBook's ISBN is %s" % self.isbn
        print "\nAlt ISBNs are %s" % self.alt_isbns
        print "\nBook's url is %s" % self.url
    def get_alt_isbns(self, code):
        alts = []
        lt = "www.librarything.com"
        get_alts = httplib.HTTPConnection(lt)
        get_alts.request("GET", "/api/thingISBN/%s" % code)
        response = get_alts.getresponse()
        parsed = etree.parse(response)
        alts = [x.text for x in parsed.findall('isbn')]
        return alts

class GenericSearch(object):
    def __init__(self, wishlist=[]):
        self.books = wishlist.books
        self.isbns = [book.alt_isbns for book in self.books] #must be a list of isbns
    def single_search(self, book, isbns=None):
        if isbns==None:
            isbns = self.isbns
        record = []
        final_record = {}
        for isbn in isbns:
            tempRecords = self.isbn_search(isbn)
            if tempRecords != None:
                for r in tempRecords:
                    record.append(r)
        if len(record) > 0:
            final_record[book.title] = record
        else:
            final_record[book.title] = [['Not available.']]
        return final_record
    def search_all(self, books=None):
        if books==None:
            books = self.books
        records = {}
        for book in books:
            record = self.single_search(book, book.alt_isbns)
            if len(record) > 0:
                records.update(record)
        if len(records) > 0:
            return records
        else:
            return None

class CarletonSearch(GenericSearch):
    def __init__(self, wishlist=[]):
        GenericSearch.__init__(self, wishlist)
    def isbn_search(self, isbn):
        url = "http://catalogue.library.carleton.ca/search/i?SEARCH=%s" % isbn
        print url
        query = urllib.urlopen(url)
        record = []
        inner_record = []
        count = 0
        parsed = lxml.html.document_fromstring(query.read())
        for td in parsed.cssselect('tr.bibItemsEntry td'):
            #strip tags & encode to ascii (from unicode)
            text = (re.sub('<[^<]+?>', '', td.text_content())).strip().encode('ascii', 'ignore')
            inner_record.append(text)
            if count == 2:
                record.append(inner_record)
                count = 0
                inner_record = []
            else:
                count += 1
        if len(record) > 0:
            return record
        else:
            return None

class WesternSearch(GenericSearch):
    def __init__(self, wishlist=[]):
        GenericSearch.__init__(self, wishlist)
    def isbn_search(self, isbn):
        url = "http://uwo.summon.serialssolutions.com/search?t.isbn=%s" % isbn
        count = 0
        record = []
        inner_record = []
        new_url = None
        try:
            query = urllib.urlopen(url)
            parsed = lxml.html.document_fromstring(query.read())
            for a in parsed.cssselect('div.previewDocumentTitle a'):
                new_url = a.get('href')
                if new_url != None:
                    newQuery = urllib.urlopen(new_url)
                    newParsed = lxml.html.document_fromstring(newQuery.read())
                    for td in newParsed.cssselect('tr.bibItemsEntry td'):
                        text = (re.sub('<[^<]+?', '', td.text_content())).strip().encode('ascii', 'ignore')
                        inner_record.append(text)
                        if count == 2:
                            record.append(inner_record)
                            inner_record = []
                            count = 0
                        else:
                            count += 1
        except httplib.HTTPException:
            pass #debug: do something here eventually
        if len(record) > 0:
            return record
        else:
            return None

class OttawaUSearch(GenericSearch):
    def __init__(self, wishlist=[]):
        GenericSearch.__init__(self, wishlist)
    def isbn_search(self, isbn):
        url = "http://orbis.uottawa.ca/search~S0/?searchtype=i&searcharg=%s&SORT=D" % isbn
        count = 0
        record = []
        inner_record = []
        query = urllib.urlopen(url)
        parsed = lxml.html.document_fromstring(query.read())
        for td in parsed.cssselect('tr.bibItemsEntry td'):
            text = (re.sub('<[^<]+?>', '', td.text_content())).strip().encode('ascii', 'ignore')
            inner_record.append(text)
            if count == 2:
                record.append(inner_record)
                inner_record = []
                count = 0
            else:
                count += 1
        if len(record) > 0:
            return record
        else:
            return None

class BrockSearch(GenericSearch):
    def __init__(self, wishlist=[]):
        GenericSearch.__init__(self, wishlist)
    def isbn_search(self, isbn):
        url = "http://catalogue.library.brocku.ca/search/a?searchtype=i&searcharg=%s&SORT=D" % isbn
        query = urllib.urlopen(url)
        record = []
        inner_record = []
        count = 0
        parsed = lxml.html.document_fromstring(query.read())
        for td in parsed.cssselect('tr.bibItemsEntry td'):
            text = (re.sub('<[^<]+?>', '', td.text_content())).strip().encode('ascii', 'ignore')
            inner_record.append(text)
            if count == 2:
                record.append(inner_record)
                count = 0
                inner_record = []
            else:
                count += 1
        if len(record) > 0:
            return record
        else:
            return None

class QueensSearch(GenericSearch):
    def __init__(self, wishlist=[]):
        GenericSearch.__init__(self, wishlist)
    def isbn_search(self, isbn):
        url = "http://queensu.summon.serialssolutions.com/search?t.isbn=%s" %isbn
        query = urllib.urlopen(url)
        record = []
        inner_record = []
        count = 0
        new_url = None
        parsed = lxml.html.document_fromstring(query.read())
        for a in parsed.cssselect('h3.resultTitle a'):
            new_url = a.get('href')
        if new_url != None:
            query2 = urllib.urlopen(new_url)
        else:
            query2 = None
        if query2 != None:
            parsed2 = lxml.html.document_fromstring(query2.read())
            for span in parsed2.cssselect('div.displayHoldings li span'):
                if span.get('class') == "subfieldData":
                    text = (re.sub('<[^<]+?', '', span.text_content())).strip().encode('ascii', 'ignore')
                    cleanText = text.replace('Show on Floorplan', '')
                    inner_record.append(cleanText)
                    if count == 2:
                        record.append(inner_record)
                        inner_record = []
                        count = 0
                    else:
                        count += 1
        if len(record) > 0:
            return record
        else:
            return None

class YorkSearch(GenericSearch):
    def __init__(self, wishlist=[]):
        GenericSearch.__init__(self, wishlist)
    def isbn_search(self, isbn):
        url = "https://www.library.yorku.ca/find/Search/Results?lookfor0%%5B%%5D=%s&lookfor0%%5B%%5D=&lookfor0%%5B%%5D=&type0%%5B%%5D=ISN&join1=AND&lookfor1%%5B%%5D=&lookfor1%%5B%%5D=&lookfor1%%5B%%5D=&type1%%5B%%5D=AllFields&join2=AND&lookfor2%%5B%%5D=&lookfor2%%5B%%5D=&lookfor2%%5B%%5D=&type2%%5B%%5D=AllFields&daterange%%5B%%5D=publishDate&publishDatefrom=&publishDateto=" % isbn
        new_url = None
        query = urllib.urlopen(url)
        record = []
        inner_record = []
        count = 0
        parsed = lxml.html.document_fromstring(query.read())
        for a in parsed.cssselect('div.resultItemLine1 a'):
            new_url = a.get('href')
        if new_url != None:
            query2 = urllib.urlopen(new_url)
        else:
            query2 = None
        if query2 != None:
            record = []
            parsed2 = lxml.html.document_fromstring(query2.read())
            for td in parsed2.cssselect('table.itemStatus tr td'):
                if (td.get('class') == "locationColumn") or (td.get('class') == "callnumColumn") or (td.get('class')=="statusColumn"):
                    text = (re.sub('<[^<]+?', '', td.text_content())).strip().encode('ascii', 'ignore')
                    inner_record.append(text)
                    if count == 2:
                        record.append(inner_record)
                        inner_record = []
                        count = 0
                    else:
                        count += 1
        if len(record) > 0:
            return record
        else:
            return None

class WindsorSearch(GenericSearch):
    def __init__(self, wishlist=[]):
        GenericSearch.__init__(self, wishlist)
    def isbn_search(self, isbn):
        url = "http://windsor.concat.ca/eg/opac/results?query=%s&qtype=keyword&locg=106&detail_record_view=1&_adv=1&page=0&sort=" % isbn
        query = urllib.urlopen(url)
        record = []
        inner_record = []
        count = 0
        parsed = lxml.html.document_fromstring(query.read())
        for td in parsed.cssselect('table.result_holdings_table tbody tr td'):
            text = (re.sub('<[^<]+?', '', td.text_content())).strip().encode('ascii', 'ignore')
            inner_record.append(text)
            if count == 3:
                record.append(inner_record)
                inner_record = []
                count = 0
            else:
                count += 1
        if len(record) > 0:
            return record
        else:
            return None

class LakeheadSearch(GenericSearch):
    def __init__(self, wishlist=[]):
        GenericSearch.__init__(self, wishlist)
    def isbn_search(self, isbn):
        print "ISBN IS %s\n" % isbn
        url = "http://inukshuk.lakeheadu.ca:7008/vwebv/search?searchArg1=%s&argType1=all&searchCode1=ISBN&recCount=10&searchType=2&page.search.search.button=Search" % isbn
        record = []
        inner_record = []
        count = 0
        try:
            query = urllib.urlopen(url)
            parsed = lxml.html.document_fromstring(query.read())
            for div in parsed.cssselect('div.oddHoldingsRow div'):
                if div.get('class')=="fieldData":
                    text = (re.sub('<[^<]+?', '', div.text_content())).strip().encode('ascii', 'ignore')
                    print text
                    inner_record.append(text)
                    if count == 2:
                        record.append(inner_record)
                        inner_record = []
                        count = 0
                    else:
                        count += 1
        except httplib.HTTPException:
            print "There was an error with URL"
            pass #do something useful here, later
        if len(record) > 0:
            return record
        else:
            return None

class RyersonSearch(GenericSearch):
    def __init__(self, wishlist=[]):
        GenericSearch.__init__(self, wishlist)
    def isbn_search(self, isbn):
        url = "http://ryerson.summon.serialssolutions.com/search?t.isbn=%s" % isbn
        record = []
        inner_record = []
        count = 0
        query = urllib.urlopen(url)
        parsed = lxml.html.document_fromstring(query.read())
        for a in parsed.cssselect('div.previewDocumentTitle a'):
            url2 = a.get('href')
            query2 = urllib.urlopen(url2)
            parsed2 = lxml.html.document_fromstring(query2.read())
            for td in parsed2.cssselect('tr.bibItemsEntry td'):
                text = (re.sub('<[^<]+?', '', td.text_content())).strip().encode('ascii', 'ignore')
                inner_record.append(text)
                if count == 2:
                    record.append(inner_record)
                    inner_record = []
                    count = 0
                else:
                    count += 1
        if len(record) > 0:
            return record
        else:
            return None

class OCADSearch(GenericSearch):
    def __init__(self, wishlist=[]):
        GenericSearch.__init__(self, wishlist)
    def isbn_search(self, isbn):
        url = "http://ipac.ocad.on.ca/ipac20/ipac.jsp?menu=search&&index=ISBNEX&term=%s" % isbn
        record = []
        inner_record = []
        query = urllib.urlopen(url)
        parsed = lxml.html.document_fromstring(query.read())
        for tr in parsed.cssselect('table.tableBackground tr'):
            for a in tr.cssselect('td a'):
                if a.get('title') == "Item Information":
                    text = (re.sub('<[^<]+?', '', a.text_content())).strip().encode('ascii', 'ignore')
                    print "Info is: %s\n" % text
                    if text == "Item Information":
                        pass
                    else:
                        inner_record.append(text)
                print "inner_record is: %s\n" % inner_record
            if len(inner_record) > 0:
                record.append(inner_record)
            inner_record = []
        if len(record) > 0:
            print "Record is %s\n" % record
            return record
        else:
            print "Record is none."
            return None

def main():
    wishlist = Wishlist("jason@wanderingrocks.com")
    search = CarletonSearch(wishlist)
    results = search.search_all()
    print results
if __name__=='__main__':
    main()
