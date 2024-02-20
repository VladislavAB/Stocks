import requests
import json
import pandas as pd
import hmac
import hashlib
from pprint import pprint


class MEXC:
    def __init__(self):
        self.base_url = 'https://api.mexc.com/api/v3/'
        self.symbols = self.get_symbols()
        self.exchange_info = self.get_exchange_info()

    def get_symbols(self) -> list:
        symbols = []
        method = 'defaultSymbols'
        url = self.base_url + method
        mexc_api_respond = requests.get(url)
        if mexc_api_respond:
            load_form_json = json.loads(mexc_api_respond.text)
            symbols = load_form_json["data"]
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
            url = self.base_url + method + "?symbol=" + pair
            mexc_api_respond = requests.get(url)
            if mexc_api_respond:
                load_form_json = json.loads(mexc_api_respond.text)
                asks = load_form_json["asks"]
            return asks
        return False

    def get_bids(self, pair: str) -> list or bool:
        if self.check_exist(pair):
            bids = []
            method = "depth"
            url = self.base_url + method + "?symbol=" + pair
            mexc_api_respond = requests.get(url)
            if mexc_api_respond:
                load_form_json = json.loads(mexc_api_respond.text)
                bids = load_form_json["bids"]
            return bids
        return False

    def get_spread(self, pair: str) -> dict:
        asks = self.get_asks(pair)
        bids = self.get_bids(pair)
        spread = {'ask': asks[0], 'bid': bids[0]}
        return spread

    def get_commission(self, pair: str) -> dict:
        commission = {}
        method = "exchangeInfo"
        url = self.base_url + method + "?symbol=" + pair
        api_respond = requests.get(url)
        if api_respond:
            load_form_json = json.loads(api_respond.text)
            maker_commission = load_form_json["symbols"][0]["makerCommission"]
            taker_commission = load_form_json["symbols"][0]["takerCommission"]
            commission = {'maker': maker_commission, 'taker': taker_commission}
        return commission

    def get_precision(self, pair):
        precision = None
        method = "exchangeInfo"
        url = self.base_url + method + "?symbol=" + pair
        api_respond = requests.get(url)
        if api_respond:
            load_form_json = json.loads(api_respond.text)
            precision = {"quotePrecision": load_form_json["symbols"][0]["quotePrecision"],
                         "quoteCommissionPrecision": load_form_json["symbols"][0]["quoteCommissionPrecision"]}
        return precision

    def get_spread_w_commission(self, pair):
        precision = self.get_precision(pair)
        spread = self.get_spread(pair)
        commission = self.get_commission(pair)
        if commission:
            commission_ask = round(float(spread['ask'][0]) * float(commission['taker']),
                                   precision["quoteCommissionPrecision"])
            commission_bid = round(float(spread['bid'][0]) * float(commission['taker']),
                                   precision["quoteCommissionPrecision"])
            spread_w_commission = {'ask': round(float(spread['ask'][0]) + commission_ask, precision["quotePrecision"]),
                                   'bid': round(float(spread['bid'][0]) - commission_bid, precision["quotePrecision"])}
            return spread_w_commission
        return spread

    def get_exchange_info(self) -> pd.DataFrame:
        method = 'exchangeInfo'
        url = self.base_url + method
        mexc_api_respond = requests.get(url)
        df = None
        if mexc_api_respond:
            exchange_info = json.loads(mexc_api_respond.text)["symbols"]
            df = pd.DataFrame(exchange_info)
            df['gen_name'] = df['symbol']
            df = df.rename(columns={'symbol': 'original_name'})
            cols = df.columns
            cols = cols.delete(list(cols).index('gen_name'))
            cols = cols.insert(0, 'gen_name')
            df = df[cols]
        return df

    @staticmethod
    def get_prices() -> pd.DataFrame:
        df = ''
        url = 'https://api.mexc.com/api/v3/ticker/bookTicker'
        api_response = requests.get(url)
        if api_response:
            load_from_json = json.loads(api_response.text)
            df = pd.DataFrame(load_from_json)
        return df

    def get_servertime(self) -> str:
        server_timestamp = None
        url = self.base_url + 'time'
        api_respond = requests.get(url)
        if api_respond:
            server_timestamp = json.loads(api_respond.text)
        server_timestamp = str(server_timestamp['serverTime'])
        return server_timestamp

    def get_currencies(self) -> pd.DataFrame:
        result = []
        url = 'https://api.mexc.com/api/v3/capital/config/getall'
        api_key = 'mx0vglgkhDEKmamyEL'
        api_secret = '6c45b7b499704760867e699d70411c0c'
        servertime = stock.get_servertime()
        prehash = f'timestamp={servertime}'
        signature = hmac.new(api_secret.encode('utf-8'), prehash.encode('utf-8'), hashlib.sha256).hexdigest()
        headers = {
            'x-mexc-apikey': api_key,
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        params = {'timestamp': str(servertime),
                  'signature': signature
                  }
        response = requests.get(url, headers=headers, params=params).json()
        for coin_info in response:
            coin = None
            name = None
            if 'coin' in coin_info.keys():
                coin = coin_info['coin']
            if 'name' in coin_info.keys():
                name = coin_info['name']
            if 'networkList' in coin_info.keys():
                for network_info in coin_info['networkList']:
                    inner_coin = None
                    depositenable = None
                    inner_name = None
                    network = None
                    withdrawenable = None
                    if 'coin' in network_info.keys():
                        inner_coin = network_info['coin']
                    if 'depositEnable' in network_info.keys():
                        depositenable = network_info['depositEnable']
                    if 'name' in network_info.keys():
                        inner_name = network_info['name']
                    if 'network' in network_info.keys():
                        network = network_info['network']
                    if 'withdrawEnable' in network_info.keys():
                        withdrawenable = network_info['withdrawEnable']
                    result.append({'coin': coin, 'name': name, 'inner_coin': inner_coin, 'inner_name': inner_name,
                                   'depositenable': depositenable,
                                   'withdrawenable': withdrawenable, 'network': network})
        df_result = pd.DataFrame(result)
        return df_result


stock = MEXC()
df_info = stock.get_exchange_info()
df_prices = stock.get_prices()
df_prices = df_prices.rename(columns={'symbol': 'original_name'})
df_final = df_prices.merge(df_info, on='original_name', how='left')
gen = df_final['gen_name']
df_final = df_final.drop('gen_name', axis=1)
df_final.insert(0, 'gen_name', gen)
df_final.to_csv('out/MEXC-spread.csv', encoding='utf-8', na_rep='None', sep='|', index=False)
stock.get_currencies().to_csv('out/MEXC-currency.csv', encoding='utf-8', na_rep='None', sep='|', index=False)
pprint(stock.get_currencies())
