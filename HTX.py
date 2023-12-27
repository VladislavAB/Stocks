import requests
import json
from datetime import datetime
import hmac
import hashlib
import base64
from urllib.parse import urlencode
from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("key_binance")
secret = os.getenv("secret_binance")


class HTX:
    def __init__(self, key, secret):
        self.base_url = 'https://api.huobi.pro/market/'
        self.symbols = self.get_symbols()
        self.access_key = key
        self.secret_key = secret

    def get_symbols(self) -> list:
        symbols = []
        method = 'tickers'
        url = self.base_url + method
        mexc_api_respond = requests.get(url)
        if mexc_api_respond:
            load_form_json = json.loads(mexc_api_respond.text)
            data = load_form_json["data"]
            for symbol in data:
                symbols.append(symbol['symbol'])
        return symbols

    def check_exist(self, pair: str) -> bool:
        if pair in self.symbols:
            return True
        else:
            print(f'Символа {pair} не сущеуствует!')
            return False

    def get_asks(self, pair: str) -> list or bool:
        if self.check_exist(pair):
            asks = []
            method = "depth"
            url = self.base_url + method + "?symbol=" + pair + "&depth=&type=step0"
            mexc_api_respond = requests.get(url)
            if mexc_api_respond:
                load_form_json = json.loads(mexc_api_respond.text)
                asks = load_form_json['tick']['asks']
            return asks
        return False

    def get_bids(self, pair: str) -> list or bool:
        if self.check_exist(pair):
            bids = []
            method = "depth"
            url = self.base_url + method + "?symbol=" + pair + "&depth=&type=step0"
            mexc_api_respond = requests.get(url)
            if mexc_api_respond:
                load_form_json = json.loads(mexc_api_respond.text)
                bids = load_form_json['tick']['bids']
            return bids
        return False

    #
    def get_spread(self, pair: str) -> dict:
        asks = self.get_asks(pair)
        bids = self.get_bids(pair)
        spread = {'ask': asks[0], 'bid': bids[0]}
        return spread

    def get_commission(self, pair: str) -> dict:
        timestamp = str(datetime.utcnow().isoformat())[0:19]
        params = urlencode({'AccessKeyId': self.access_key,
                            'SignatureMethod': 'HmacSHA256',
                            'SignatureVersion': '2',
                            'Timestamp': timestamp,
                            'symbols': pair
                            })
        method = 'GET'
        endpoint = '/v2/reference/transact-fee-rate'
        base_uri = 'api.huobi.pro'
        pre_signed_text = method + '\n' + base_uri + '\n' + endpoint + '\n' + params
        hash_code = hmac.new(self.secret_key.encode(), pre_signed_text.encode(), hashlib.sha256).digest()
        signature = urlencode({'Signature': base64.b64encode(hash_code).decode()})
        url = 'https://' + base_uri + endpoint + '?' + params + '&' + signature
        response = requests.request(method, url)
        accts = json.loads(response.text)
        maker_commission = accts['data'][0]['makerFeeRate']
        taker_commission = accts['data'][0]['takerFeeRate']
        commission = {'maker': maker_commission, 'taker': taker_commission}
        return commission


load_dotenv()
htx_key = os.getenv("key_HTX")
htx_secret = os.getenv("secret_HTX")

stock = HTX(htx_key, htx_secret)
print(stock.get_symbols())
print(stock.check_exist('sylousdt'))
print(stock.get_asks("sylousdt"))
print(stock.get_bids("sylousdt"))
print(stock.get_spread("sylousdt"))
print(stock.get_commission("sylousdt"))
