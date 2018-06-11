from bs4 import BeautifulSoup
import requests
from multiprocessing import Pool
from itertools import repeat

from currency import get_USD_rate
import re
from re import sub
from decimal import Decimal
import json

USD_to_other_rates = dict()


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
    return json.load(open('rates.txt','r'))

def get_price(price_div):
    price = None

    currency = price_div.find(
        'span',
        {'itemprop': 'priceCurrency'}
    )['content']

    price_div_text = price_div.text.split('\r')[0].replace('\n', ' ').strip()

    if currency != 'USD':
        prog = re.compile(r'(\(([^\)]+)\))')
        m = prog.findall(price_div_text)
        if m:
            currency = 'USD'
            price = ' '.join(map(lambda l: l[1],m))
            # price = {
            #     currency:' '.join(map(lambda l: l[1],m))
            #     }
    # else:
    #     # price = {
    #     #     currency:price_div_text
    #     # }
    #     price = price_div_text
    if price is None:
        price = price_div_text

    if currency == 'USD':
        prog = re.compile(r'(\$ (\d+[,]*\d+))')
        m = prog.findall(price)
        print('{} - {}'.format(price, m))

    return price
    # return prog.findall(p)


    current_price = price_div.find(
        'span',
        {'itemprop': 'price'}
    ).text.strip()
    # current_price = float(prog.search(current_price).group(0))
    current_price = float(sub(r'[^\d.]', '', current_price))
    price[currency] = {
        'current': current_price,
    }
    # if this item is on sale
    original_price = price_div.find(
        'span',
        {'class': 'text-secondary text-linethrough'}
    )
    if original_price is not None:
        original_price = original_price.text.strip()
        # original_price = float(prog.search(original_price).group(0))
        original_price = float(sub(r'[^\d.]', '', original_price))
        price[currency]['original'] = original_price

    '''
    If the currency not in USD, then convert the price to USD
    '''
    if currency != 'USD':
        if currency not in USD_to_other_rates:
            USD_to_other_rates[currency] = get_USD_rate(currency)
        rate = USD_to_other_rates[currency]
        current_price_USD = current_price/rate
        price['USD'] = {
            'current': current_price_USD
        }
        if original_price is not None:
            original_price_USD = original_price/rate
            price['USD']['original'] = original_price_USD
    return price

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
            # print(country['name'],price_div.text.replace('\n', ' '))
            # return
            # currency = price_div.find(
            #     'span',
            #     {'itemprop': 'priceCurrency'}
            # )['content']
            # current_price = price_div.find(
            #     'span',
            #     {'itemprop': 'price'}
            # ).text.strip()
            # # if this item is on sale
            # original_price = price_div.find(
            #     'span',
            #     {'class': 'text-secondary text-linethrough'}
            # )
            # if original_price is not None:
            #     original_price = original_price.text.strip()
            # print('Site {country} - PRICE: {price} - SIZE AVAIABLE: {sizes}'.format(
            #     country=country['name'],
            #     sizes=' - '.join(map(lambda size: size['title'], sizes)),
            #     price='({}) {}{}'.format(
            #         currency,
            #         '{} -> '.format(original_price) if original_price is not None else '',
            #         current_price
            #     ).strip()
            # ))

            price = get_price(price_div)
            # return
            # print('Site {}:'.format(country['name']))
            # # if price:
            #     # print('Site {}: {}'.format(country['name'], price))
            # # return 'Site {}: {} {}'.format(country['name'], price[])
            # for currency in price:
            #     print('{}: {}'.format(currency, price[currency]))
        else:
            print('Site {} NOT AVAILABLE'.format(country['name']))


def check_size_wrapper(args):
    return check_size(*args)


def main():
    item_code = '41753815EK'
    countries = get_countries()
    print('There are {} countr{}'.format(
        len(countries),
        'ies' if len(countries) > 1 else 'y'
    ))
    with Pool(processes=10) as pool:
        # args = ((country, item_code) for country in countries)
        results = pool.map(
            check_size_wrapper,
            zip(
                countries,
                repeat(item_code)
            )
        )
        # for r in results:
        #     print(r)
        pool.close()
        pool.join()


if __name__ == '__main__':
    main()
