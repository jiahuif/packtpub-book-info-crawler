import requests
from pyquery import PyQuery as pq
import sqlite3
import sys

session = requests.Session()

def crawl_single_book(book_url):
  r = session.get(book_url)
  r.raise_for_status()
  page_html = r.text
  doc = pq(page_html)
  block = doc(".overview_right .inner")
  block('h3').remove()
  book_info_array = map (lambda a: map(lambda s: s.strip() , pq(a).text().split(':')) , block.html().split('<br/>'))
  book_info = dict(book_info_array)
  book_info['Title'] = doc('#content-header h1').text()
  return book_info

def init_database(db_file = 'database.db'):
  conn = sqlite3.connect(db_file)
  cur = conn.cursor()
  cur.execute('CREATE TABLE IF NOT EXISTS books(isbn text PRIMARY KEY, isbn13 text UNIQUE, title text, author text, releaseDate text)')
  conn.commit()
  return conn

def save_book_info_to_db(conn, book_info):
  cur = conn.cursor()
  cur.execute("SELECT * FROM books WHERE isbn = ?" , (book_info['ISBN'] , ))
  if len(cur.fetchall()):
    return
  cur.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?)", (book_info['ISBN'] , book_info['ISBN 13'] , book_info['Title'] , book_info['Author(s)'] , book_info['Release Date']) )
  conn.commit()
conn = init_database()
try:
  page = 0
  while True:
    listing_url = "http://www.packtpub.com/books?page=%d" % page
    print >> "Listing url:",sys.stderr, listing_url
    r = session.get(listing_url)
    r.raise_for_status()
    listing_html = r.text
    doc = pq(listing_html)
    doc.make_links_absolute(listing_url)
    link_elements = doc(".content .view-content .views-field-title a[href$='book']")
    links = link_elements.map(lambda i , e: pq(e).attr('href'))
    for link in links:
      while True:
        try:
          book_info = crawl_single_book(link)
          save_book_info_to_db(conn, book_info)
          break
        except Exception as ex:
          print >> sys.stderr, "Failed to process url:", link, ex, "Retrying..."
    page += 1
finally:
  conn.close()
