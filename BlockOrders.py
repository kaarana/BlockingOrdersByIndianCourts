import json
import logging
import time

import requests
import waybackpy
from bs4 import BeautifulSoup
from waybackpy import exceptions

SERVER_URL = 'https://dot.gov.in'
PAGE_URL = '/blocking-notificationsinstructions-internet-service-licensees-under-court-orders'
FEED_URL = 'https://dot.gov.in/taxonomy/term/2883/feed'
BLOCK_ORDER_PAGES = 6


def write_json(new_data, filename):
    with open(filename, 'w') as file:
        json.dump(new_data, file, indent=4)


def archive_url(url):
    logging.info('archiving url ' + url)
    user_agent = "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0"
    wayback = waybackpy.Url(url, user_agent)
    try:
        oldest_archive = wayback.oldest()
        return oldest_archive.archive_url
    except:
        logging.debug('Exception retriving older archive data for url ' + url)
        pass
    try:
        wayback.save()
        return wayback.archive_url
    except:
        logging.info('Exception in saving ' + url + ' to archive')
        pass
        return 'NO_ARCHIVE_AVAILABLE'


def get_all_block_orders():
    blockorders = []

    for page in range(0, BLOCK_ORDER_PAGES + 1):
        url = SERVER_URL + PAGE_URL + '?page=' + str(page)
        soup = BeautifulSoup(requests.get(url).text, 'lxml')
        orders = soup.find_all('article')
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
            except:
                logging.info('Exception processing order')
                pass

    write_json(blockorders, 'BlockOrders.json')


def main():
    get_all_block_orders()


if __name__ == "__main__":
    logging.basicConfig(filename='BlockOrders' + time.strftime("%Y%m%d-%H%M%S") +
                        '.log', format='%(asctime)s %(message)s', level=logging.INFO)
    main()
