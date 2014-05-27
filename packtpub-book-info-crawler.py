import requests
from pyquery import PyQuery as pq
import sqlite3
import sys

session = requests.Session()

def crawl_single_book(book_url):
  try:
    r = session.get(book_url)
    r.raise_for_status()
    page_html = r.text
    doc = pq(page_html)
    block = doc(".overview_right .inner")
    block('h3').remove()
    book_info_array = map (lambda a: map(lambda s: s.strip() , pq(a).text().split(':')) , block.html().split('<br/>'))
    book_info = dict(book_info_array)
    return book_info
  except:
    print >> sys.stderr, "Error processing: " + book_url
page = 0
while True:
  listing_url = "http://www.packtpub.com/books?page=%d" % page
  print >> sys.stderr, listing_url
  r = session.get(listing_url)
  r.raise_for_status()
  listing_html = r.text
  doc = pq(listing_html)
  doc.make_links_absolute(listing_url)
  link_elements = doc(".content .view-content .views-field-title a[href$='book']")
  links = link_elements.map(lambda i , e: pq(e).attr('href'))
  for link in links:
    book_info = crawl_single_book(link)
    print book_info['ISBN']
  page += 1
