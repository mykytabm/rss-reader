import requests
from bs4 import BeautifulSoup


def scrape(url: str):
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, features='xml')
        articles = soup.findAll('item')
        article_list = []
        for a in articles:
            title = a.find('title').text
            link = a.find('link').text
            published = a.find('pubDate').text
            article = {
                'title': title,
                'link': link,
                'published': published
            }
            article_list.append(article)

        return article_list

    except Exception as e:
        print('The scraping job failed. See exception: ')
        print(e)
