import pandas as pd
import requests
import json


class EXMO:
    def __init__(self):
        self.base_url = 'https://api.exmo.me/v1.1/'
        self.symbols = self.get_symbols()
        self.exchange_info = self.get_exchange_info()  # return dataframe

    #
    def get_symbols(self) -> list:
        symbols = []
        method = 'ticker'
        url = self.base_url + method
        mexc_api_respond = requests.get(url)
        if mexc_api_respond:
            load_form_json = json.loads(mexc_api_respond.text)
            symbols = list(load_form_json.keys())
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
            method = "order_book"
            url = self.base_url + method + "?pair=" + pair + '&limit=10'
            mexc_api_respond = requests.get(url)
            if mexc_api_respond:
                load_form_json = json.loads(mexc_api_respond.text)
                asks = load_form_json[pair]['ask']
            return asks
        return False

    def get_bids(self, pair: str) -> list or bool:
        if self.check_exist(pair):
            bids = []
            method = "order_book"
            url = self.base_url + method + "?pair=" + pair + '&limit=10'
            mexc_api_respond = requests.get(url)
            if mexc_api_respond:
                load_form_json = json.loads(mexc_api_respond.text)
                bids = load_form_json[pair]['bid']
            return bids
        return False

    def get_spread(self, pair: str) -> dict:
        asks = self.get_asks(pair)
        bids = self.get_bids(pair)
        spread = {'ask': asks[0], 'bid': bids[0]}
        return spread

    def get_commission(self, pair: str) -> dict:
        commission = {}
        method = "pair_settings"
        url = self.base_url + method
        api_respond = requests.get(url)
        if api_respond:
            load_form_json = json.loads(api_respond.text)
            maker_commission = load_form_json[pair]["commission_maker_percent"]
            taker_commission = load_form_json[pair]["commission_taker_percent"]
            commission = {'maker': maker_commission, 'taker': taker_commission}
        return commission

    def get_precision(self, pair) -> dict:
        precision = None
        method = "pair_settings"
        url = self.base_url + method
        api_respond = requests.get(url)
        if api_respond:
            load_form_json = json.loads(api_respond.text)
            precision = load_form_json[pair]["price_precision"]
        return {"precision_inst": precision,
                "precision_commission": precision}

    def get_spread_w_commission(self, pair):
        precision = self.get_precision(pair)
        spread = self.get_spread(pair)
        commission = self.get_commission(pair)
        commission_ask = round(float(spread['ask'][0]) * float(commission['taker']), precision['precision_commission'])
        commission_bid = round(float(spread['bid'][0]) * float(commission['taker']), precision['precision_commission'])
        spread_w_commission = {'ask': round(float(spread['ask'][0]) + commission_ask, precision['precision_inst']),
                               'bid': round(float(spread['bid'][0]) - commission_bid, precision['precision_inst'])}
        return spread_w_commission

    def get_pairs(self):
        pairs = None
        method = "pair_settings"
        url = self.base_url + method
        api_respond = requests.get(url)
        if api_respond:
            load_form_json = json.loads(api_respond.text)
            pairs = list(load_form_json.keys())
        return pairs

    def get_prices(self):
        prices = []
        pairs = self.get_pairs()
        for pair in pairs:
            print(pair)
            best_ask = self.get_asks(pair)[0]
            best_bid = self.get_bids(pair)[0]
            prices.append({'original_name': pair, 'best_ask': best_ask[0], 'quantity_ask': best_ask[1],
                           'best_bid': best_bid[0], 'quantity_bid': best_bid[1]})
        prices = pd.DataFrame(prices)
        return prices

    def get_exchange_info(self) -> pd.DataFrame:
        method = 'pair_settings'
        url = self.base_url + method
        mexc_api_respond = requests.get(url)
        exchange_info = ''
        if mexc_api_respond:
            exchange_info = json.loads(mexc_api_respond.text)
            for pair in exchange_info.keys():
                exchange_info[pair]['gen_name'] = pair.replace('_', '')
        df = pd.DataFrame(exchange_info)
        df = df.T
        df['original_name'] = df.index
        cols = df.columns
        cols = cols.delete(list(cols).index('gen_name'))
        cols = cols.delete(list(cols).index('original_name'))
        cols = cols.insert(0, 'original_name')
        cols = cols.insert(0, 'gen_name')
        df = df[cols]
        return df


stock = EXMO()
df_info = stock.get_exchange_info()
df_prices = stock.get_prices()
df_final = df_prices.merge(df_info, on='original_name', how='left')
gen = df_final['gen_name']
df_final = df_final.drop('gen_name', axis=1)
df_final = df_final.drop('time', axis=1)
df_final.insert(0, 'gen_name', gen)
df_final.to_csv('out/list-EXMO.csv', encoding='utf-8', na_rep='None', sep='|', index=False)

