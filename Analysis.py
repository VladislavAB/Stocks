import pandas as pd

df_BIT = pd.read_csv('out/list-BIT.csv', delimiter='|')
df_EXMO = pd.read_csv('out/list-EXMO.csv', delimiter='|')
df_HTX = pd.read_csv('out/list-HTX.csv', delimiter='|')
df_MEXC = pd.read_csv('out/list-MEXC.csv', delimiter='|')
df_OKX = pd.read_csv('out/list-OKX.csv', delimiter='|')
gen_names = list(set(list(df_BIT["gen_name"]) + list(df_EXMO["gen_name"]) + list(df_HTX["gen_name"]) + list(
    df_MEXC["gen_name"]) + list(df_OKX["gen_name"])))
df_final = pd.DataFrame({'gen_name': gen_names})

names_BIT = df_BIT[["gen_name", "original_name"]]
names_EXMO = df_EXMO[["gen_name", "original_name"]]
names_HTX = df_HTX[["gen_name", "original_name"]]
names_MEXC = df_MEXC[["gen_name", "original_name"]]
names_OKX = df_OKX[["gen_name", "original_name"]]
df_final = df_final.merge(df_BIT[["gen_name", "original_name"]], on='gen_name', how='left')
df_final = df_final.rename(columns={"original_name": 'name_BIT'})
df_final = df_final.merge(df_EXMO[["gen_name", "original_name"]], on='gen_name', how='left')
df_final = df_final.rename(columns={"original_name": 'name_EXMO'})
df_final = df_final.merge(df_HTX[["gen_name", "original_name"]], on='gen_name', how='left')
df_final = df_final.rename(columns={"original_name": 'name_HTX'})
df_final = df_final.merge(df_OKX[["gen_name", "original_name"]], on='gen_name', how='left')
df_final = df_final.rename(columns={"original_name": 'name_OKX'})
df_final = df_final.merge(df_OKX[["gen_name", "original_name"]], on='gen_name', how='left')
df_final = df_final.rename(columns={"original_name": 'name_MEXC'})
df_final.to_csv('out/Catalog.csv', encoding='utf-8', na_rep='None', sep='|')
available_tokens = df_final[
    df_final["name_BIT"].notna() & df_final["name_EXMO"].notna() & df_final["name_HTX"].notna() & df_final[
        "name_OKX"].notna() & df_final["name_MEXC"].notna()]
print(available_tokens)
