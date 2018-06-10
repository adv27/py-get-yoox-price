import requests

API = 'http://apilayer.net/api/live?access_key={}&currencies={}&source=USD'
ACCESS_KEY = ''

def get_access_key():
    pass

def get_USD_rate(currency_code):
    url = API.format(ACCESS_KEY, currency_code)
    r = requests.get(url)
    result = r.json()
    return result['quotes']['USD{}'.format(currency_code)]
