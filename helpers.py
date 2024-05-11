import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def get_root_url(url):
    """
    Extracts the root URL from a given URL by removing any path segments and query parameters.
    """
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme if parsed_url.scheme else 'https'
    netloc = parsed_url.netloc if parsed_url.netloc else parsed_url.path.split('/')[0]
    root_url = f'{scheme}://{netloc}'
    return root_url


def get_full_path(url):
    """
    Takes a URL as input and returns a string with the domain and path parts joined by dashes.
    """
    # Remove the scheme (http:// or https://) from the URL
    if url.startswith('http://'):
        url = url[7:]
    elif url.startswith('https://'):
        url = url[8:]

    # Remove any trailing slashes (/) from the URL
    url = url.rstrip('/')

    # Replace any remaining slashes (/) with dashes (-)
    url = url.replace('/', '-')

    return url


def get_base_url(url):
    """
    Extracts the base URL from a given URL by removing the protocol and any path segments.
    """
    parsed_url = urlparse(url)
    base_url = parsed_url.netloc
    if base_url.startswith('www.'):
        base_url = base_url[4:]
    return base_url


def get_all_sitemap_urls(base_url, sitemap_url):
    """
    Recursively fetches all sitemap URLs from the provided sitemap URL.
    Returns a list of all site URLs found in the sitemaps.
    """
    site_urls = []
    response = requests.get(sitemap_url)
    soup = BeautifulSoup(response.text, 'xml')
    sitemap_tags = soup.find_all('sitemap')
    for sitemap_tag in sitemap_tags:
        loc_tag = sitemap_tag.find('loc')
        if loc_tag:
            sitemap_url = urljoin(base_url, loc_tag.text)
            sitemap_url = sitemap_url.strip()
            site_urls += get_all_sitemap_urls(base_url, sitemap_url)
    urlset_tags = soup.find_all('urlset')
    for urlset_tag in urlset_tags:
        url_tags = urlset_tag.find_all('url')
        for url_tag in url_tags:
            loc_tag = url_tag.find('loc')
            if loc_tag:
                loc_tag_text = loc_tag.text.strip()
                site_urls.append(loc_tag_text)
    return site_urls


def get_all_sites(base_url):
    """
    Fetches all sitemap URLs from the base URL and recursively fetches all site URLs from the sitemaps.
    Returns a list of all site URLs found.
    """
    site_urls = []
    if not base_url.startswith('http') and not base_url.startswith('https'):
        base_url = 'https://' + base_url
    sitemap_url = urljoin(base_url, '/sitemap.xml')
    site_urls += get_all_sitemap_urls(base_url, sitemap_url)
    return site_urls
