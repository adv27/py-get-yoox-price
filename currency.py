import requests
from config import ACCESS_KEY
import sys
import json

API = 'http://apilayer.net/api/live?access_key={}&currencies={}&source=USD'

def get_USD_rate(currency_code):
    url = API.format(ACCESS_KEY, currency_code)
    r = requests.get(url)
    result = r.json()
    return result['quotes']

def main():
    currencies = sys.argv[1:]
    rates = get_USD_rate(','.join(currencies).upper())
    json.dump(rates, open('rates.txt','w'))

if __name__ == '__main__':
    main()
