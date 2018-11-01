import json
import re
import sys
from decimal import Decimal
<<<<<<< HEAD
from io import StringIO
from itertools import repeat
from multiprocessing import Pool
from re import sub

import requests
from bs4 import BeautifulSoup


class Country(object):
    def __init__(self, url, name):
        self.url = url
        self.name = name
        if self.name == 'CHINA':
            self.url = 'https://www.yoox.com/cn'
        self.code = self.url.split('/')[-1]

    def __repr__(self):
        return '{} - {}'.format(self.name, self.code)


class Size(object):
    def __init__(self, default_label, alternative_label, quantity):
        self.default_label = default_label
        self.alternative_label = alternative_label
        self.quantity = quantity

    def __repr__(self):
        return '{}{}{}'.format(
            self.default_label.ljust(50),
            self.alternative_label.ljust(50),
            self.quantity
        )


class Item(object):
    STT_SOLDOUT = 0
    STT_AVAILABLE = 1
    STT_NOT_AVAILABLE = 2

    def __init__(self, country, code):
        self.country = country
        self.code = code

        self.__page = self.__get_page()
        self.__soup = BeautifulSoup(self.__page.content, 'html.parser')
        self.__html_code = self.__page.content.decode('utf-8')

        self.status = self.STT_NOT_AVAILABLE
        if self.__soup.select('div.itemSoldOutMessage'):
            self.status = self.STT_SOLDOUT
        elif self.__soup.select('div#itemColors'):
            self.status = self.STT_AVAILABLE
            self.price = self.__get_price_EUR()
            self.promo = self.__get_promotion()
            self.sizes = self.__get_sizes()

    def __get_page(self):
        URL = '{country}/{code}/item'
        url = URL.format(country=self.country.url, code=self.code)
        # proxy_dict = {'http' :'10.22.194.32:8080','https' :'10.22.194.32:8080'}
        # r = requests.get(url, proxies=proxy_dict)
        r = requests.get(url)
        return r

    def __get_price_EUR(self):
        pattern = r'\["product_discountprice_EUR"\] = "(\d*.?\d*)"'
        match = re.search(pattern, self.__html_code)
        price_in_EUR = match.group(1)
        return price_in_EUR

    def __get_promotion(self):
        promo = self.__soup.find('div', {'class': 'box-highlighted font-sans text-size-default default-padding text-primary'})
        if promo:
            return promo.text.strip()
        return None

    def __get_sizes(self):
        pattern = r'jsInit.item.colorSizeJson = (.*?);'
        matches = re.search(pattern, self.__html_code)
        match = matches.group(1)
        color_size_json = json.loads(match)
        sizes = color_size_json['Sizes']
        qty = color_size_json['Qty']

        size_list = list()

        for size in sizes:
            q = list(filter(lambda qq: qq.split('_')[-1] == str(size['Id']), qty))
            if q:
                size.update({
                    'Qty': qty[q[0]]
                })
                s = Size(size['DefaultSizeLabel'], size['AlternativeSizeLabel'], size['Qty'])
                size_list.append(s)

        return size_list
=======
import json
import sys
>>>>>>> 0c1fbeb66c4b1ef0bcce3e63aa82f0078ab67429


def get_countries():
    countries = list()
    html = ''
    with open('country_list_html.html', 'r') as file:
        # with open('country_list_short.html', 'r') as file:
        for line in file:
            html += line
    soup = BeautifulSoup(html, 'html.parser')
    anchors = soup.find_all('a', {'class': 'js-track-me js-switchcountry'})
    for a in anchors:
        countries.append(Country(a['href'], a['title']))
    return countries


<<<<<<< HEAD
def printer(item):
    pp = StringIO()
    print(''.ljust(100, '-'), file=pp)
    print(item.country, file=pp)
    if item.status == Item.STT_AVAILABLE:
        print('AVAILABLE', file=pp)
        print('{}{}'.format('PRICE'.ljust(30, '-'), item.price), file=pp)
        if item.promo:
            print('PROMOTION: {}'.format(item.promo), file=pp)
        for size in item.sizes:
            print(size, file=pp)
    elif item.status == Item.STT_SOLDOUT:
        print('SOLDOUT :(', file=pp)
    elif item.status == Item.STT_NOT_AVAILABLE:
        print('NOT AVAILBLE', file=pp)
    print(''.ljust(100, '-'), file=pp)
    return pp.getvalue()


def check_size(country, item_code):
    item = Item(country=country, code=item_code)
    return item
    # printer(item)


def check_size_wrapper(args):
    i = check_size(*args)
    return printer(i)


def main():
    if len(sys.argv) == 2:
        item_code = sys.argv[1]
        # country = Country('https://www.yoox.com/us', 'UNITED STATES')
        # check_sizee(country, item_code)
        # return
        countries = get_countries()
        print('There are {} countr{}'.format(
            len(countries),
            'ies' if len(countries) > 1 else 'y'
        ))

        with Pool(processes=10) as pool:
            results = pool.map(
                check_size_wrapper,
                zip(countries, repeat(item_code))
            )
            pool.close()
            pool.join()
            for r in results:
                print(r)
    else:
        print('Please provide item code!!!')
=======
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
>>>>>>> 0c1fbeb66c4b1ef0bcce3e63aa82f0078ab67429


if __name__ == '__main__':
    main()
