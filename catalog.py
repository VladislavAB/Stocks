import pandas as pd


def none_count(x):
    count = 0
    for i in x:
        if str(i) == 'nan':
            count += 1
    return count


# ------------------
# and_matches = df_final[
#     df_final["name_BIT"].notna() & df_final["name_EXMO"].notna() & df_final["name_HTX"].notna() & df_final[
#         "name_OKX"].notna() & df_final["name_MEXC"].notna()]
# or_matches = df_final[
#     df_final["name_BIT"].notna() | df_final["name_EXMO"].notna() | df_final["name_HTX"].notna() | df_final[
#         "name_OKX"].notna() | df_final["name_MEXC"].notna()]
# ------------------

df_BIT = pd.read_csv('out/list-BIT.csv', delimiter='|')
df_EXMO = pd.read_csv('out/list-EXMO.csv', delimiter='|')
df_HTX = pd.read_csv('out/list-HTX.csv', delimiter='|')
df_MEXC = pd.read_csv('out/list-MEXC.csv', delimiter='|')
df_OKX = pd.read_csv('out/list-OKX.csv', delimiter='|')
gen_names = {
    'gen_name': list(set(list(df_BIT["gen_name"]) + list(df_EXMO["gen_name"]) + list(df_HTX["gen_name"]) + list(
        df_MEXC["gen_name"]) + list(df_OKX["gen_name"])))}
df_final = pd.DataFrame(gen_names)
df_final = df_final.merge(df_BIT[["gen_name", "original_name"]], on='gen_name', how='left')
df_final = df_final.rename(columns={"original_name": 'name_BIT'})
df_final = df_final.merge(df_EXMO[["gen_name", "original_name"]], on='gen_name', how='left')
df_final = df_final.rename(columns={"original_name": 'name_EXMO'})
df_final = df_final.merge(df_HTX[["gen_name", "original_name"]], on='gen_name', how='left')
df_final = df_final.rename(columns={"original_name": 'name_HTX'})
df_final = df_final.merge(df_OKX[["gen_name", "original_name"]], on='gen_name', how='left')
df_final = df_final.rename(columns={"original_name": 'name_OKX'})
df_final = df_final.merge(df_MEXC[["gen_name", "original_name"]], on='gen_name', how='left')
df_final = df_final.rename(columns={"original_name": 'name_MEXC'})

df_final['count_none'] = df_final.apply(none_count, axis=1)
two_more_matches = df_final[df_final['count_none'] <= 3]
two_more_matches.to_csv('out/catalog.csv', encoding='utf-8', na_rep='None', sep='|', index=False)
