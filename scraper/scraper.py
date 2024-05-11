import os
import time
import argparse
import concurrent.futures
from termcolor import colored
import math
from tqdm import tqdm
from scraper.helpers import get_all_sites, get_full_path, get_root_url, get_base_url, fetch_website_info, save_text, save_file, fetch_reader_info
from scraper.constants import Constants

def fetch_page(url, directory, current, total, debug, reader):
    try:
        print(f'Fetching page {current + 1} / {total}: {url}') if debug else None
        start_time = time.time()
        if reader:
            text = fetch_reader_info(url)
            if text is None:
                return
            filename = get_full_path(url) + '.md'
            save_file(text, directory, filename)          
        else:
            soup = fetch_website_info(url)
            if soup is None:
                return
            filename = get_full_path(url) + '.txt'
            save_text(soup, directory, filename)
        end_time = time.time()
        if debug:
            print(f'Fetched and saved {url} in {"{:.2f}".format(end_time - start_time)} seconds.')
    except Exception as e:
        print(colored(f'Error fetching page {url}: {e}', 'red'))

class Scraper:
    def __init__(self):
        parser = argparse.ArgumentParser(description='Fetch and save website pages.')
        parser.add_argument('--url', type=str, help='Website URL to scrape')
        parser.add_argument('--no-limit', '-nl', action='store_true', help='fetch all available pages')
        parser.add_argument('--debug', '-d', action='store_true', help='Enable debug output')
        parser.add_argument('--reader', '-r', action='store_true', help='Enable reader mode')
        self.parser = parser

    def run(self):
        args = self.parser.parse_args()
        if not args.url:
            url = input('Enter website URL: ')
        self.url = args.url or url
        self.num_pages = None if args.no_limit else Constants['MAX_PAGES']
        self.debug = args.debug
        self.reader = args.reader
        self.fetch_pages(self.url, self.num_pages, debug=self.debug)

    def fetch_pages(self, url, num_pages, max_workers=None, debug=False):
        try:
            start_time = time.time()
            root_url = get_root_url(url)
            base_url = get_base_url(root_url)
            print("Fetching pages from '{}'...".format(base_url))
            directory = os.path.join('public', base_url)
            os.makedirs(directory, exist_ok=True)
            site_urls = get_all_sites(base_url)
            total_urls = len(site_urls)

            DEFAULT_PAGES = Constants['MAX_PAGES']
            print("Found {} pages.".format(total_urls))
            if total_urls > DEFAULT_PAGES and num_pages is not None:
                num_pages = input('Enter number of pages to scrape (default: {}): '.format(DEFAULT_PAGES))
                num_pages = int(num_pages) if num_pages else Constants['MAX_PAGES']

            num_pages = min(num_pages, total_urls) if num_pages else total_urls

            if max_workers is None:
                max_workers = min(math.ceil(num_pages / 10), 10)

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(fetch_page, site_urls[i], directory, i, num_pages, debug, self.reader) for i in range(num_pages)]
                list(tqdm(concurrent.futures.as_completed(futures), total=num_pages))

            end_time = time.time()
            total_time = end_time - start_time
            print(colored(f'{num_pages} pages fetched and saved to {directory}. Total time: {total_time:.2f} seconds.', 'green'))
            left_pages = total_urls - num_pages
            print(colored(f'Leaving {total_urls - num_pages} pages.', 'yellow')) if left_pages else None
        except Exception as e:
            print(colored(f'Error fetching pages: {e}', 'red'))

