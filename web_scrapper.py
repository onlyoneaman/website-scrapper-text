import os
import requests
from bs4 import BeautifulSoup
from helpers import get_all_sites, get_full_path, get_root_url, get_base_url
import time
import argparse
import concurrent.futures
from termcolor import colored
import math
from tqdm import tqdm


def fetch_website_info(url):
    """
    Fetches website info and returns the BeautifulSoup object.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def save_text(soup, directory, filename):
    """
    Extracts the text from the website and saves it to a file in the specified directory.
    """
    text = soup.get_text()
    with open(os.path.join(directory, filename), 'w', encoding='utf-8') as file:
        file.write(text)


def fetch_page(url, directory, current, total, debug):
    print(f'Fetching page {current + 1} / {total}: {url}') if debug else None
    start_time = time.time()
    soup = fetch_website_info(url)
    filename = get_full_path(url) + '.txt'
    save_text(soup, directory, filename)
    end_time = time.time()
    print(f'Fetched and saved {url} in {"{:.2f}".format(end_time - start_time)} seconds.') if debug else None


def fetch_pages(base_url, num_pages, max_workers=None,debug=False):
    """
    Fetches the specified number of pages from the site and saves them to files in a directory named after the base URL.
    """
    start_time = time.time()
    directory = os.path.join('public', get_base_url(base_url))
    os.makedirs(directory, exist_ok=True)
    site_urls = get_all_sites(base_url)
    total_urls = len(site_urls)
    num_pages = num_pages if num_pages else total_urls
    num_pages = min(num_pages, total_urls)
    left_pages = (total_urls - num_pages) > 0
    print(colored('Fetching {} pages from {}...'.format(num_pages, base_url), 'yellow'))
    print(colored(f'Leaving {total_urls - num_pages} pages.', 'yellow')) if left_pages else None

    if max_workers is None:
        max_workers = min(math.ceil(num_pages / 10), 10)
        max_workers = max(max_workers, 100)

    print(colored('Using {} workers.'.format(max_workers), 'yellow'))

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for url_index in range(num_pages):
            url = site_urls[url_index]
            futures.append(executor.submit(fetch_page, url, directory, url_index, total_urls, debug))
        for future in tqdm(concurrent.futures.as_completed(futures), total=num_pages):
            future.result()
    end_time = time.time()
    total_time = "{:.2f}".format(end_time - start_time)
    print(colored(f'{num_pages} pages fetched and saved to public/{get_base_url(base_url)} directory.', 'green'))
    print(colored(f'Total time taken: {total_time} seconds.', 'green'))


def main():
    parser = argparse.ArgumentParser(description='Fetch website pages and create knowledge base')
    parser.add_argument('url', metavar='URL', type=str, nargs='?', const=None, help='website URL')
    parser.add_argument('--no-limit', '-nl', action='store_true', help='fetch all available pages')
    parser.add_argument('--debug', '-d', action='store_true', help='shows all debug messages')
    args = parser.parse_args()
    url = args.url
    debug = args.debug
    num_pages = None
    if not url:
        url = input('Enter website URL: ')
    if args.no_limit is False:
        num_pages = input('Enter number of pages (default: 100): ')
        num_pages = int(num_pages) if num_pages else 100
    if url is None or url == '':
        print(colored('URL cannot be empty.', 'red'))
        return
    base_url = get_root_url(url)
    print("Fetching pages from '{}'...".format(base_url))
    fetch_pages(base_url, num_pages, debug=debug)


if __name__ == '__main__':
    main()
