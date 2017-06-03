from bs4 import BeautifulSoup
from collections import defaultdict
import requests
import json
import string
import sys


def build_corpus(page_links):
    corpus = defaultdict(int)
    for index, page_url in enumerate(page_links):
        document_words = set()
        for p in BeautifulSoup(requests.get(page_url).text, "html.parser").select("#maincontent p"):
            for word in "".join(c for c in p.text.lower() if c in string.whitespace + string.ascii_lowercase).split():
                document_words.add(word)

        for word in document_words:
            corpus[word] += 1
        print(100 * index / len(page_links), "%")

    with open("corpus.json", "w") as f:
        json.dump(corpus, f)


ROOT_URL = "https://courses.grad.ucl.ac.uk/lista-z.pht?option=az"
PAGE_LINKS = ["https://courses.grad.ucl.ac.uk/" + a['href']
              for a in BeautifulSoup(requests.get(ROOT_URL).text, "html.parser")
                  .select("#maincontent a")]


def build_pages(page_links):
    pages = []
    for page_url in page_links:
        web_page = BeautifulSoup(requests.get(page_url).text, "html.parser")
        page = {
            "title": web_page.select_one("#maincontent h1").text,
            "url": page_url,
            "summary": "\n".join(p.text for p in web_page.select("#maincontent p")),
        }
        pages.append(page)
        print(page)
    with open("pages.json", "w") as f:
        json.dump(pages, f)

def evaluate_page(page, f_corpus, query):
    search_prio = 0
    if page["title"] == query:
        search_prio = 1
    for word in query.lower().split():
        if word in page["title"].lower():
            search_prio += 4 * (1/f_corpus[word])

        if word in page["summary"].lower():
            search_prio += 1 * (1/f_corpus[word])

    return search_prio

if __name__ == '__main__':
    PAGES = []
    CORPUS = []
    while 1:
        command = input("\\ ").strip()
        if command == "search":
            query = input("? ").strip()
            print(sorted(PAGES, key=lambda page: -evaluate_page(page, None, query))[:20])
        if command == "build":
            build_pages(PAGE_LINKS)
            build_corpus(PAGE_LINKS)
        if command == "build_pages":
            build_pages(PAGE_LINKS)
        if command == "build_corpus":
            build_corpus(PAGE_LINKS)
        if command == "load":
            with open("pages.json", "r") as pages:
                with open("corpus.json", "r") as corpus:
                    PAGES, CORPUS = json.load(pages), json.load(corpus)

        if command == "debug":
            print(PAGES[5:10])
        if command == "quit":
            sys.exit(0)
