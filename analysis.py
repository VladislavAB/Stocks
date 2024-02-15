import pandas as pd


def min_ask(x):
    keys = x.keys()
    asks = []
    for key in keys:
        if 'ask' in key:
            stock = key.split('_')[-1]
            if str(x[key]) == 'nan':
                pass
            else:
                ask = x[key]
                asks.append({"stock": stock, "ask": ask})
    asks = pd.DataFrame(asks)
    min_ask = asks[asks["ask"] == asks["ask"].min()]
    min_ask_price = min_ask["ask"].values[0]
    min_ask_stock = min_ask["stock"].values[0]
    return min_ask_price, min_ask_stock


def max_bid(x):
    keys = x.keys()
    bids = []
    for key in keys:
        if 'bid' in key:
            stock = key.split('_')[-1]
            if str(x[key]) == 'nan':
                pass
            else:
                bid = x[key]
                bids.append({"stock": stock, "bid": bid})
    bids = pd.DataFrame(bids)
    max_bid = bids[bids["bid"] == bids["bid"].max()]
    max_bid_price = max_bid["bid"].values[0]
    max_bid_stock = max_bid["stock"].values[0]
    return max_bid_price, max_bid_stock


df_BIT = pd.read_csv('out/list-BIT.csv', delimiter='|')
df_EXMO = pd.read_csv('out/list-EXMO.csv', delimiter='|')
df_HTX = pd.read_csv('out/list-HTX.csv', delimiter='|')
df_MEXC = pd.read_csv('out/list-MEXC.csv', delimiter='|')
df_OKX = pd.read_csv('out/list-OKX.csv', delimiter='|')
df_final = pd.read_csv('out/catalog.csv', delimiter='|')
df_final = df_final.drop('name_BIT', axis=1)
df_final = df_final.drop('name_EXMO', axis=1)
df_final = df_final.drop('name_HTX', axis=1)
df_final = df_final.drop('name_OKX', axis=1)
df_final = df_final.drop('name_MEXC', axis=1)
df_final = df_final.drop('count_none', axis=1)
df_final = df_final.merge(df_BIT[["gen_name", "best_bid", 'best_ask']], on='gen_name', how='left')
df_final = df_final.rename(columns={"best_ask": 'best_ask_BIT'})
df_final = df_final.rename(columns={"best_bid": 'best_bid_BIT'})
df_final = df_final.merge(df_EXMO[["gen_name", "best_ask", 'best_bid']], on='gen_name', how='left')
df_final = df_final.rename(columns={"best_ask": 'best_ask_EXMO'})
df_final = df_final.rename(columns={"best_bid": 'best_bid_EXMO'})
df_final = df_final.merge(df_HTX[["gen_name", "bid", 'ask']], on='gen_name', how='left')
df_final = df_final.rename(columns={"bid": 'best_bid_HTX'})
df_final = df_final.rename(columns={"ask": 'best_ask_HTX'})
df_final = df_final.merge(df_OKX[["gen_name", "askPx", 'bidPx']], on='gen_name', how='left')
df_final = df_final.rename(columns={"askPx": 'best_ask_OKX'})
df_final = df_final.rename(columns={"bidPx": 'best_bid_OKX'})
df_final = df_final.merge(df_MEXC[["gen_name", "bidPrice", 'askPrice']], on='gen_name', how='left')
df_final = df_final.rename(columns={"askPrice": 'best_ask_MEXC'})
df_final = df_final.rename(columns={"bidPrice": 'best_bid_MEXC'})
df_final['min_ask'] = df_final.apply(min_ask, axis=1)
df_final['max_bid'] = df_final.apply(max_bid, axis=1)
df_final["arbitrage"] = df_final.apply(lambda x: x["max_bid"][0] - x["min_ask"][0], axis=1)
df_final['percent'] = df_final.apply(lambda x: x["arbitrage"] * 100 / x["min_ask"][0], axis=1)
df_final.to_csv('out/arbitrage.csv', encoding='utf-8', na_rep='None', sep='|', index=False)
print(df_final)
