import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import colorama

colorama.init()

BLUE = colorama.Fore.BLUE
GREEN = colorama.Fore.GREEN
RED = colorama.Fore.RED
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW

internal_urls = set()
wiki_source = ''

def get_links(url, target):
    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    links = []
    found = None
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None or ':' in href or href.startswith(wiki_source) :
            # href empty tag
            continue
        # join the URL if it's relative (not absolute link)
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        # remove URL GET parameters, URL fragments, etc.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        if not (bool(urlparse(href).netloc) and bool(urlparse(href).scheme)):
            # not a valid URL
            continue
        if href in internal_urls:
            # already in the set
            continue
        internal_urls.add(href)
        links.append(href)
        if href == target:
            found = href
            break

    return (found, links)

def crawl(url, target, max_urls, query_urls):
    if max_urls == 0:
        return False

    (found, links) = get_links(url, target)

    if found is not None:
        print(f"{GREEN}[!] Article connection found! {RESET}")
        for url in query_urls:
            print(f"- {url}")
        print(f"- {found}")
        return True

    for link in links:
        query_urls.append(link)
        if crawl(link, target, max_urls-1, query_urls):
            return True
        query_urls.pop()

    return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Wikipedia crawler that will find a connection between article A and B.")
    parser.add_argument("article_a", help="Article name A.")
    parser.add_argument("article_b", help="Article name B.")
    parser.add_argument("-w", "--wiki-source", help="", default="https://de.wikipedia.org/wiki/", type=str)
    parser.add_argument("-m", "--max-urls", help="Number of max URLs to crawl.", default=50, type=int)

    args = parser.parse_args()
    wiki_source = args.wiki_source
    article_a = wiki_source + args.article_a
    article_b = wiki_source + args.article_b
    max_urls = args.max_urls

    internal_urls.add(article_a)

    if not crawl(article_a, article_b, max_urls, [article_a]):
        print(f"{RED}[!] Articles aren't connected. {RESET}")

