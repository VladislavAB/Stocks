import requests
import json
from dotenv import load_dotenv
import os
import datetime
import hmac
import base64
import pandas as pd
from pprint import pprint


class OKX:
    def __init__(self):
        self.base_url = 'https://www.okx.com/api/v5/market/'
        self.symbols = self.get_symbols()
        self.exchange_info = self.get_exchange_info()

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
    def signature(timestamp, method, request_path, secret_key, body=None):
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

    def get_exchange_info(self) -> pd.DataFrame:
        url = 'https://www.okx.com/api/v5/public/instruments?instType=SPOT'
        mexc_api_respond = requests.get(url)
        exchange_info = ''
        if mexc_api_respond:
            exchange_info = json.loads(mexc_api_respond.text)['data']
        df = pd.DataFrame(exchange_info)
        df['gen_name'] = df['instId'].apply(lambda x: x.replace('-', ''))
        df = df.rename(columns={'instId': 'original_name'})
        cols = df.columns
        cols = cols.delete(list(cols).index('gen_name'))
        cols = cols.delete(list(cols).index('original_name'))
        cols = cols.insert(0, 'original_name')
        cols = cols.insert(0, 'gen_name')
        df = df[cols]
        return df

    def get_prices(self) -> pd.DataFrame:
        df = ''
        url = 'https://www.okx.com/api/v5/market/tickers?instType=SPOT'
        api_response = requests.get(url)
        if api_response:
            load_from_json = json.loads(api_response.text)['data']
            df = pd.DataFrame(load_from_json)
        return df

    def get_currencies(self) -> pd.DataFrame:
        result = []
        url = 'https://www.okx.com/api/v5/asset/currencies'
        request = 'GET'
        endpoint = '/api/v5/asset/currencies'
        header = dict()
        time = self.get_time()
        header['CONTENT-TYPE'] = 'application/json'
        header['OK-ACCESS-KEY'] = okex_key
        header['OK-ACCESS-SIGN'] = self.signature(time, request, endpoint, okex_secret)
        header['OK-ACCESS-TIMESTAMP'] = str(time)
        header['OK-ACCESS-PASSPHRASE'] = okex_pass
        response = requests.get(url, headers=header)
        api_response = response.json()['data']
        for coin_info in api_response:
            currency = None
            chain = None
            name = None
            deposit_enable = None
            withdraw_enable = None
            if 'canDep' in coin_info.keys():
                deposit_enable = coin_info['canDep']
            if 'ccy' in coin_info.keys():
                currency = coin_info['ccy']
            if 'chain' in coin_info.keys():
                chain = coin_info['chain']
            if 'canWd' in coin_info.keys():
                withdraw_enable = coin_info['canWd']
            if 'name' in coin_info.keys():
                name = coin_info['name']
            result.append({'currency': currency, 'chain': chain, 'name': name, 'deposit_enable': deposit_enable,
                           'withdraw_enable': withdraw_enable})
        df_result = pd.DataFrame(result)
        return df_result


load_dotenv()
okex_key = os.getenv("key_OKX")
okex_secret = os.getenv("secret_OKX")
okex_pass = os.getenv("pass_OKX")

stock = OKX()
df_prices = stock.get_prices()
df_info = stock.get_exchange_info()
df_prices = df_prices.rename(columns={'instId': 'original_name'})
df_final = df_prices.merge(df_info, on='original_name', how='left')
gen = df_final['gen_name']
df_final = df_final.drop('gen_name', axis=1)
df_final = df_final.drop('instType_x', axis=1)
df_final.insert(0, 'gen_name', gen)
df_final.to_csv('out/OKX-spread.csv', encoding='utf-8', na_rep='None', sep='|', index=False)
stock.get_currencies().to_csv('out/OKX-currency.csv', encoding='utf-8', na_rep='None', sep='|', index=False)
