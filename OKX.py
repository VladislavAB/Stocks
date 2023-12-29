import requests
import json
from dotenv import load_dotenv
import os
import datetime
import hmac
import base64


class OKX:
    def __init__(self):
        self.base_url = 'https://www.okx.com/api/v5/market/'
        self.symbols = self.get_symbols()

    def get_symbols(self) -> list:
        symbols = []
        method = 'tickers?instType=SPOT'
        url = self.base_url + method
        mexc_api_respond = requests.get(url)
        if mexc_api_respond:
            load_form_json = json.loads(mexc_api_respond.text)
            data = load_form_json["data"]
            for symbol in data:
                symbols.append(symbol['instId'])
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
            method = "books"
            url = self.base_url + method + "?instId=" + pair + '&sz=10'
            mexc_api_respond = requests.get(url)
            if mexc_api_respond:
                load_form_json = json.loads(mexc_api_respond.text)
                asks = load_form_json["data"][0]['asks']
            return asks
        return False

    def get_bids(self, pair: str) -> list or bool:
        if self.check_exist(pair):
            bids = []
            method = "books"
            url = self.base_url + method + "?instId=" + pair + '&sz=10'
            mexc_api_respond = requests.get(url)
            if mexc_api_respond:
                load_form_json = json.loads(mexc_api_respond.text)
                bids = load_form_json["data"][0]['bids']
            return bids
        return False

    def get_spread(self, pair: str) -> dict:
        asks = self.get_asks(pair)
        bids = self.get_bids(pair)
        spread = {'ask': asks[0][:2], 'bid': bids[0][:2]}
        return spread

    @staticmethod
    def get_time():
        now = datetime.datetime.utcnow()
        t = now.isoformat("T", "milliseconds")
        return t + "Z"

    @staticmethod
    def signature(timestamp, method, request_path, body, secret_key):
        if str(body) == '{}' or str(body) == 'None':
            body = ''
        message = str(timestamp) + str.upper(method) + request_path + str(body)
        mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
        d = mac.digest()
        return base64.b64encode(d)

    def get_commission(self, pair: str):
        url = 'http://www.okex.com/api/v5/account/trade-fee?instType=SPOT&instId=' + pair
        # Make headers & signature
        request = 'GET'
        endpoint = '/api/v5/account/trade-fee'
        body = '?instType=SPOT&instId=' + pair
        header = dict()
        time = self.get_time()
        header['CONTENT-TYPE'] = 'application/json'
        header['OK-ACCESS-KEY'] = okex_key
        header['OK-ACCESS-SIGN'] = self.signature(time, request, endpoint, body, okex_secret)
        header['OK-ACCESS-TIMESTAMP'] = str(time)
        header['OK-ACCESS-PASSPHRASE'] = okex_pass
        response = requests.get(url, headers=header)
        api_response = response.json()
        maker_commission = api_response["data"][0]["maker"]
        taker_commission = api_response["data"][0]["taker"]
        commission = {'maker': abs(float(maker_commission)), 'taker': abs(float(taker_commission))}
        return commission

    def get_spread_w_commission(self, pair):
        precision = 10
        spread = self.get_spread(pair)
        commission = self.get_commission(pair)
        commission_ask = round(float(spread['ask'][0]) * float(commission['taker']), precision)
        commission_bid = round(float(spread['bid'][0]) * float(commission['taker']), precision)
        spread_w_commission = {'ask': round(float(spread['ask'][0]) + commission_ask, precision),
                               'bid': round(float(spread['bid'][0]) - commission_bid, precision)}
        return spread_w_commission


load_dotenv()
okex_key = os.getenv("key_OKX")
okex_secret = os.getenv("secret_OKX")
okex_pass = os.getenv("pass_OKX")

stock = OKX()
print(stock.get_spread("MDT-USDT"))
print(stock.get_commission("MDT-USDT"))
print(stock.get_spread_w_commission("MDT-USDT"))
