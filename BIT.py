import requests
import json
import pandas as pd


class BIT:
    def __init__(self):
        self.base_url = 'https://api.bit.com/spot/v1/'
        self.symbols = self.get_symbols()
        self.exchange_info = self.get_exchange_info()

    def get_symbols(self) -> list:
        symbols = []
        method = 'instruments'
        url = self.base_url + method
        mexc_api_respond = requests.get(url)
        if mexc_api_respond:
            load_form_json = json.loads(mexc_api_respond.text)
            for symbol in load_form_json["data"]:
                symbols.append(symbol['pair'])
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
            method = "orderbooks"
            url = self.base_url + method + "?pair=" + pair + '&level=10'
            mexc_api_respond = requests.get(url)
            if mexc_api_respond:
                load_form_json = json.loads(mexc_api_respond.text)
                asks = load_form_json["data"]['asks']
            return asks
        return False

    def get_bids(self, pair: str) -> list or bool:
        if self.check_exist(pair):
            bids = []
            method = "orderbooks"
            url = self.base_url + method + "?pair=" + pair + '&level=10'
            mexc_api_respond = requests.get(url)
            if mexc_api_respond:
                load_form_json = json.loads(mexc_api_respond.text)
                bids = load_form_json["data"]["bids"]
            return bids
        return False

    def get_spread(self, pair: str) -> dict:
        asks = self.get_asks(pair)
        bids = self.get_bids(pair)
        spread = {'ask': asks[0], 'bid': bids[0]}
        return spread

    def get_commission(self, pair: str) -> dict:
        commission = {}
        method = "instruments"
        url = self.base_url + method
        api_respond = requests.get(url)
        if api_respond:
            load_form_json = json.loads(api_respond.text)
            for i in load_form_json['data']:
                if i['pair'] == pair:
                    maker_commission = load_form_json['data'][0]["maker_fee_rate"]
                    taker_commission = load_form_json['data'][0]["taker_fee_rate"]
                    commission = {'maker': maker_commission, 'taker': taker_commission}
        return commission

    def get_bases(self) -> list:
        bases = None
        method = "instruments"
        url = self.base_url + method
        api_respond = requests.get(url)
        if api_respond:
            load_form_json = json.loads(api_respond.text)
            df = pd.DataFrame(load_form_json['data'])
            bases = list(set(list(df['quote_currency'])))
        return bases

    def get_prices(self) -> pd.DataFrame:
        bases = self.get_bases()
        base_url = 'https://api.bit.com/spot/v1/market/summary?quote_ccy='
        prices = []
        for base in bases:
            url = base_url + base
            api_response = requests.get(url)
            if api_response:
                load_form_json = json.loads(api_response.text)
                prices.append(pd.DataFrame(load_form_json['data']))
        prices = pd.concat(prices)
        return prices

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
        method = 'instruments'
        url = self.base_url + method
        mexc_api_respond = requests.get(url)
        exchange_info = ''
        if mexc_api_respond:
            exchange_info = json.loads(mexc_api_respond.text)['data']
        df = pd.DataFrame(exchange_info)
        df['gen_name'] = df['pair'].apply(lambda x: x.replace('-', ''))
        df = df.rename(columns={'pair': 'original_name'})
        cols = df.columns
        cols = cols.delete(list(cols).index('gen_name'))
        cols = cols.insert(0, 'gen_name')
        df = df[cols]
        return df


stock = BIT()
df_info = stock.get_exchange_info()
df_prices = stock.get_prices()
df_prices = df_prices.rename(columns={'pair': 'original_name'})
df_final = df_prices.merge(df_info, on='original_name', how='left')
df_final = df_final[df_final["best_bid"] != '']
gen = df_final['gen_name']
df_final = df_final.drop('gen_name', axis=1)
df_final = df_final.drop('time', axis=1)
df_final.insert(0, 'gen_name', gen)
df_final.to_csv('out/list-BIT.csv', encoding='utf-8', na_rep='None', sep='|', index=False)
