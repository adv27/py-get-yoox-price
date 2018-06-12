from bs4 import BeautifulSoup
import requests
from multiprocessing import Pool
from itertools import repeat

from currency import get_USD_rate
import re
from re import sub
from decimal import Decimal
import json
import sys


def get_countries():
    countries = list()
    html = ''
    with open('country_list_html.html', 'r') as file:
        for line in file:
            html += line
    soup = BeautifulSoup(html, 'html.parser')
    anchors = soup.find_all('a', {'class': 'js-track-me js-switchcountry'})
    for a in anchors:
        countries.append({
            'url': a['href'],
            'name': a['title']
        })
    return countries


def get_rates():
    return json.load(open('rates.txt', 'r'))


def get_price(price_div):
    price = None
    current_price_USD = None
    original_price_USD = None

    # get the currency of the displayed price
    currency = price_div.find(
        'span',
        {'itemprop': 'priceCurrency'}
    )['content']

    # text of the price div, remove 'tax included' part
    price_div_text = price_div.text.split('\r')[0].replace('\n', ' ').strip()

    if currency != 'USD':
        prog = re.compile(r'(\(([^\)]+)\))')
        m = prog.findall(price_div_text)
        if m:
            currency = 'USD'
            price = ' '.join(map(lambda l: l[1], m))

    if price is None:
        price = price_div_text

    if currency == 'USD':
        prog = re.compile(r'(\$ ((\d+[,|.]*)+))')
        m = prog.findall(price)
        # print('{} - {}'.format(price, m))
        if len(m) == 2:
            # the item is on sale
            original_price_USD = m[0][1]
            current_price_USD = m[1][1]
        else:
            current_price_USD = m[0][1]
        return {
            'USD': {
                'current': current_price_USD,
                'original': original_price_USD
            }
        }

    return None


def get_size(item_size_div):
    sizes = item_size_div.find_all('li')
    # filter sold out size
    sizes = filter(lambda size: 'disabled' not in size['class'], sizes)
    return sizes


def check_size(country, item_code):
    URL = '{country}/{code}/item'
    if country['name'] == 'CHINA':
        country['url'] = 'https://www.yoox.com/cn'
    url = URL.format(country=country['url'], code=item_code)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    soldout = soup.find('div', {'class': 'soldout'})
    if soldout is not None:
        print('Site {} SOLD OUT :('.format(country['name']))
    else:
        item_sizes = soup.find('div', {'id': 'itemSizes'})
        if item_sizes is not None:
            sizes = item_sizes.find_all('li')
            # filter sold out size
            # sizes = filter(lambda size: 'disabled' not in size['class'], sizes)
            item_detail_div = soup.find('div', {'id': 'js-item-details'})
            price_div = item_detail_div.find('div', {'id': 'item-price'})
            price = get_price(price_div)
            if price:
                return {
                    'country': country['name'],
                    'price': price
                }
            else:
                return None
        else:
            print('Site {} NOT AVAILABLE'.format(country['name']))


def check_size_wrapper(args):
    return check_size(*args)


def main():
    countries = get_countries()
    print('There are {} countr{}'.format(len(countries), 'ies' if len(countries) > 1 else 'y'))
    codes = sys.argv[1:]
    for item_code in codes:
        with Pool(processes=10) as pool:
            results = pool.map(check_size_wrapper, zip(countries, repeat(item_code)))
            for r in results:
                if r:
                    print(r['country'], end=' :')
                    price = r['price']
                    for currency in price:
                        pp = price[currency]
                        if pp['original'] is not None:
                            # this item is on sale
                            print('{} ==> {}'.format(pp['original'], pp['current']))
                        else:
                            # this item not on sale
                            print('{}'.format(pp['current']))
            pool.close()
            pool.join()


if __name__ == '__main__':
    main()
