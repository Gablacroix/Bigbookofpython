import requests
from bs4 import BeautifulSoup

URL = 'https://fgis.gost.ru/fundmetrology/cm/results?filter_org_title=%D0%94%D0%B8%D1%80%D0%B5%D0%BA%D1%86%D0%B8%D1%8F%20%D0%BF%D0%BE%20%D1%80%D0%B5%D0%BC%D0%BE%D0%BD%D1%82%D1%83%20%D1%82%D1%8F%D0%B3%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D0%BE%D0%B4%D0%B2%D0%B8%D0%B6%D0%BD%D0%BE%D0%B3%D0%BE%20%D1%81%D0%BE%D1%81%D1%82%D0%B0%D0%B2%D0%B0&filter_mi_modification=%D0%91%D0%AD%D0%9B-%D0%A3&sort=org_title%7Casc&rows=100&activeYear=2021'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0', 'accept':'*/*' }

def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r

def parse():
    html = get_html(URL)
    print(html)


parse()
