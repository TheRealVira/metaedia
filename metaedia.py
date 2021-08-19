import requests, time, colorama, argparse, re

colorama.init()

GREEN = colorama.Fore.GREEN
RED = colorama.Fore.RED
RESET = colorama.Fore.RESET

discovered_urls = set()
wiki_source = ""
wiki_prefix = ""
start_time = time.time()
url_journey = []
HTML_TAG_REGEX = re.compile(r"<a[^<>] ?href=([\'\"])(.*?)\1", re.IGNORECASE)


def get_links(url, target):
    links = []
    found = None
    for a_tag in HTML_TAG_REGEX.findall(requests.get(url).text):
        href = f"{wiki_source}{a_tag[1]}"
        if (
            href in discovered_urls
            or ":" in a_tag[1]
            or not a_tag[1].startswith(wiki_prefix)
        ):
            continue

        discovered_urls.add(href)
        links.append(href)
        if href == target:
            found = href
            break

    return (found, links)


def crawl(url, target, max_urls):
    currentLinkslist = [url]
    for i in range(1, max_urls):
        links = []
        lastlink = ""
        for link in currentLinkslist:
            (found, links) = get_links(link, target)
            lastlink = link
            if found is not None:
                url_journey.append(lastlink)
                return True
        currentLinkslist = links
        url_journey.append(lastlink)

    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Wikipedia crawler that will find a connection between article A and B."
    )
    parser.add_argument("article_a", help="Article name A.")
    parser.add_argument("article_b", help="Article name B.")
    parser.add_argument(
        "-w",
        "--wiki-source",
        help="Wikipedia base URL.",
        default="https://de.wikipedia.org",
        type=str,
    )
    parser.add_argument(
        "-p",
        "--wiki-prefix",
        help="Wikipedia article prefix.",
        default="/wiki/",
        type=str,
    )
    parser.add_argument(
        "-m", "--max-urls", help="Number of max URLs to crawl.", default=50, type=int
    )

    args = parser.parse_args()
    wiki_source = args.wiki_source
    wiki_prefix = args.wiki_prefix
    article_a = "".join([wiki_source, wiki_prefix, args.article_a])
    article_b = "".join([wiki_source, wiki_prefix, args.article_b])
    max_urls = args.max_urls

    discovered_urls.add(article_a)
    if crawl(article_a, article_b, max_urls):
        print(f"{GREEN}[!] Article connection found! {RESET}")
        for url in url_journey:
            print(f"- {url}")
        print(f"- {article_b}")
    else:
        print(f"{RED}[!] Articles aren't connected. {RESET}")

    print(f"---- metaedia took {time.time() - start_time} seconds to complete! ----")