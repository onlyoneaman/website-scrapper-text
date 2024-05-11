### Simple Python Website Knowledge Base

Enter your website name, and the knowledge base will be created for you.

## How to use

1. Clone the repository
```
git clone git@github.com:onlyoneaman/website-scrapper-text.git
```

2. Install the requirements
```
pip install -r requirements.txt
```

3. Run the script
```
python -m scraper --url
```

4. Enter the website name
```
Enter website URL: https://www.shopufy.com
Enter number of pages (default: 100): 200
```

![img.png](static/img.png)

5. The knowledge base will be created in the `public` folder with your website name.


## Options

1. Pass the website name  as arguments.

```
python -m scraper --url https://www.shopify.com
```

2. Scrape all the pages of the website. (Default: 100)

```
python -m scraper --no-limit
```
