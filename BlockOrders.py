import json
import glob
import logging
import time

import feedparser
import requests
import waybackpy
from bs4 import BeautifulSoup
from waybackpy import exceptions

SERVER_URL = 'https://dot.gov.in'
PAGE_URL = '/blocking-notificationsinstructions-internet-service-licensees-under-court-orders'
FEED_URL = 'https://dot.gov.in/taxonomy/term/2883/feed'
BLOCK_ORDER_PAGES = 20
DATA_FILE = "data/BlockingOrders.json"


def incremental_feed_update():
    logging.log(logging.INFO, 'start of incremental_feed_update')
    feed = feedparser.parse(FEED_URL)
    new_orders = []
    with open(DATA_FILE, "r") as file:
        data = json.load(file)
    for entry in feed.entries:
        order = [element for element in data if element['link'] == entry.link]
        if (len(order) > 0):
            break
        else:
            new_orders.append(entry.link)
    logging.log(logging.INFO, "New orders count " + str(len(new_orders)))
    if (len(new_orders) > 0):
        get_all_block_orders()


def write_json(new_data, filename):
    with open(filename, 'w') as file:
        json.dump(new_data, file, indent=4)


def archive_url(url):
    logging.log(logging.INFO, 'archiving url ' + url)
    user_agent = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    wayback = waybackpy.Url(url, user_agent)
    try:
        oldest_archive = wayback.oldest()
        return oldest_archive.archive_url
    except:
        logging.log(logging.DEBUG,
                    'Exception retriving older archive data for url ' + url)
        pass
    try:
        wayback.save()
        return wayback.archive_url
    except:
        logging.log(logging.INFO, 'Exception in saving ' + url + ' to archive')
        pass
        return 'NO_ARCHIVE_AVAILABLE'


def get_all_block_orders(incremental_feed_update=True):
    logging.log(logging.INFO, 'start of get_all_block_orders')
    blockorders = []

    for page in range(0, BLOCK_ORDER_PAGES + 1):
        logging.log(logging.DEBUG, page)
        url = SERVER_URL + PAGE_URL + '?page=' + str(page)
        logging.log(logging.DEBUG, url)
        soup = BeautifulSoup(requests.get(url).text, 'lxml')
        if (page == 0 and not incremental_feed_update):
            try:
                BLOCK_ORDER_PAGES = soup.find(
                    'li', attrs={'class': 'pager-last last'}).find('a')['href'].split('=')[1]
            except:
                BLOCK_ORDER_PAGES = 20

        orders = soup.find('div', attrs={'role': 'main'}).find_all(
            'div', attrs={'class': 'node-data-services'})
        for article in orders:
            order = {}
            try:
                ordersoup = BeautifulSoup(str(article), 'lxml')
                order['title'] = ordersoup.find(
                    'h2', attrs={'class': 'node__title node-title'}).text.strip()
                order['date'] = ordersoup.find(
                    'div', attrs={'class': 'author-name-published-date'}).text.strip()
                order['link'] = SERVER_URL + ordersoup.find(
                    'h2', attrs={'class': 'node__title node-title'}).find('a')['href']
                order['link_archive'] = archive_url(order['link'])
                order['order_pdf'] = BeautifulSoup(requests.get(order['link']).text, 'lxml').select(
                    'a[type*="application/pdf"]')[0]['href'].split('?download=1')[0]
                order['order_pdf_archive'] = archive_url(order['order_pdf'])
                blockorders.append(order)
                logging.log(logging.DEBUG, order)
            except:
                logging.log(logging.INFO, 'Exception processing order')
                pass
        if not incremental_feed_update:
            write_json(blockorders, 'BlockOrders_' + str(page) + '.json')

    if not incremental_feed_update:
        json_objects = []
        for filename in glob.glob("BlockOrders_*.json"):
            with open(filename, "r") as f:
                data = json.load(f)
                json_objects += data
    else:
        logging.log(logging.INFO, "Incremental update")
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
        json_objects = blockorders + data

        # Deduplicate the list
        json_objects = [dict(t)
                        for t in {tuple(d.items()) for d in json_objects}]

    with open(DATA_FILE, "w") as file:
        json.dump(json_objects, file)


def main():
    # get_all_block_orders(incremental_feed_update=False)
    incremental_feed_update()


if __name__ == "__main__":
    logging.basicConfig(filename='BlockOrders' + time.strftime("%Y%m%d-%H%M%S") +
                        '.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
    main()
