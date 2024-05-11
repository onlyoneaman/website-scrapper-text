from setuptools import setup, find_packages

setup(
    name='website_scraper',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'concurrent',
        'termcolor',
        'tqdm',
    ],
    entry_points={
        'console_scripts': [
            'scraper=scraper.scraper:main',
        ],
    }
)
