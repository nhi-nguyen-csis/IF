from urllib.request import urlopen
from urllib.parse import urljoin # convert relateive url to absolute url
from bs4 import BeautifulSoup 
from collections import deque # creating request queue - frontier
from pymongo import MongoClient 
import re # find html and shtml in the retrieved links


def connectDataBase():
    # Creating a database connection object using pymongo
    DB_NAME = "CS_CPP"
    DB_HOST = "localhost"
    DB_PORT = 27017
    try:
        client = MongoClient(host=DB_HOST, port=DB_PORT)
        db = client[DB_NAME]
        return db
    except:
        print("Database not connected successfully")

def storePage(documents, url, html):
  # value to be inserted
  page = {"url": url, "html": html}
  documents.insert_one(page)

def flagTargetPage(documents, url):
  update = {"$set": {"isTargetPage": True}}
  documents.update_one({"url": url}, update)

# Helper func: to retrieve the HTML content of a URL
def retrieve_html(url):
  try:
    response = urlopen(url)
    html = response.read()
    return html
  except Exception as e:
    print(f"Error retrieving {url}: {e}")
    return None

# Helper func: to check if href is html or shtml link
def is_html_or_shtml(href):
  is_html = re.match(r'^https?:\/\/', href)
  is_shmtl = re.match(r'[^"]+\.shtml', href)
  return is_html or is_shmtl

# Helper func: to check if it's our target page
def is_target_page(bs):
  h1_tag = bs.find("h1", {"class": "cpp-h1"})
  return h1_tag and h1_tag.text == "Permanent Faculty"

def crawling():
  # connect to the database
  db = connectDataBase()
  # create a collection
  documents = db["CS_CPP_pages"]
  while frontier:
    url = frontier.popleft()
    if url in visited: continue
    visited.add(url)

    # retrieve html content
    html = retrieve_html(url)
    bs = BeautifulSoup(html, 'html.parser')

    # store the url and html into the database
    storePage(documents, url, html)

    # check if the current page is the target page 
    if is_target_page(bs): 
      flagTargetPage(documents, url)
      # print(f"FOUND TARGET - page: {url}") # testing
      frontier.clear()
    else:
      # extracting all the URLs found within a page’s <a> tags:
      for link in bs.find_all('a'):
        href = link.get('href')
        if not is_html_or_shtml(href): continue
        # convert relative url into absolute url 
        link['href'] = urljoin(BASE_URL, link['href'])
        frontier.append(link['href'])

if __name__ == "__main__":
  CS_HOME_PAGE = "https://www.cpp.edu/sci/computer-science/"
  BASE_URL = "https://www.cpp.edu" # to convert relative url into absolute url
  frontier = deque()
  frontier.append(CS_HOME_PAGE)
  visited = set()
  crawling()
