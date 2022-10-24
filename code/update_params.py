import pandas as pd
import numpy as np
import gspread


def get_records(sheet_name):
    '''Pass the name of the Google Spreadsheet containing EpiCollect records
    and returns two Pandas dataframes, one for Passaporti and one for Rinnovi'''
    gc = gspread.oauth()
    sh = gc.open(sheet_name)
    worksheet_list = sh.worksheets()
    pass_id = []
    rinn_id = []
    for wks in worksheet_list: 
        if wks.title.startswith("Passaporti"):
            pass_id.append(wks.id)
        if wks.title.startswith("Rinnovi"): 
            rinn_id.append(wks.id)
    for i in range(len(pass_id)): 
        if i == 0: 
            id_passaporti = pass_id[i]
            ws_passaporti = sh.get_worksheet_by_id(id_passaporti)
            df_passaporti = pd.DataFrame(ws_passaporti.get_all_records())
        else: 
            id_passaporti = pass_id[i]
            ws_passaporti = sh.get_worksheet_by_id(id_passaporti)
            df_passaporti = df_passaporti.append(ws_passaporti.get_all_records())
    for i in range(len(rinn_id)): 
        if i == 0: 
            id_rinnovi = rinn_id[i]
            ws_rinnovi = sh.get_worksheet_by_id(id_rinnovi)
            df_rinnovi = pd.DataFrame(ws_rinnovi.get_all_records())
        else: 
            id_rinnovi = rinn_id[i]
            ws_rinnovi = sh.get_worksheet_by_id(id_rinnovi)
            df_rinnovi = df_rinnovi.append(ws_rinnovi.get_all_records())
    df_passaporti, df_rinnovi = df_passaporti.replace("", np.nan), df_rinnovi.replace("", np.nan)
    df_passaporti, df_rinnovi = df_passaporti.replace("#N/A", np.nan), df_rinnovi.replace("#N/A", np.nan)
    df_passaporti, df_rinnovi = df_passaporti.replace("Caricamento in corso...", np.nan), df_rinnovi.replace("Caricamento in corso...", np.nan)
    df_passaporti, df_rinnovi = df_passaporti.dropna(how='all'), df_rinnovi.dropna(how="all")
    df_passaporti.data, df_passaporti.data_nascita, df_rinnovi.data_rinnovo = df_passaporti.data.fillna(0), df_passaporti.data_nascita.fillna(0), df_rinnovi.data_rinnovo.fillna(0)
    df_passaporti.data, df_passaporti.data_nascita, df_rinnovi.data_rinnovo = df_passaporti.data.astype(int),  df_passaporti.data_nascita.astype(int), df_rinnovi.data_rinnovo.astype(int)
    df_passaporti, df_rinnovi = df_passaporti.reset_index(), df_rinnovi.reset_index()
    return df_passaporti, df_rinnovi


def get_records_params(sheet_name):
    gc = gspread.oauth()
    sh = gc.open(sheet_name)
    worksheet_list = sh.worksheets()
    wks_id = []
    for wks in worksheet_list: 
        wks_id.append(wks.id)
    for i in range(len(wks_id)): 
        if i == 0: 
            id_spr = wks_id[i]
            ws = sh.get_worksheet_by_id(id_spr)
            df = pd.DataFrame(ws.get_all_records())
        else: 
            id_spr = wks_id[i]
            ws = sh.get_worksheet_by_id(id_spr)
            df = df.append(ws.get_all_records())
    df = df.replace("", np.nan)
    df = df.replace("Caricamento in corso...", np.nan)
    df = df.replace("#N/A", np.nan)
    df= df.dropna(how='all')
    df.data_nascita=  df.data_nascita.fillna(0)
    df.data_nascita= df.data_nascita.astype(int)
    df = df.reset_index().drop(columns="index")
    return df
    
    
def update_params():
    df_passaporti, df_rinnovi = get_records("EpiCollect - Risposte")
    ids_records = df_passaporti.ec5_uuid.values
    df_params = get_records_params("params - Nati in trentino")
    ids_params = df_params.ec5_uuid.values
    new = list(set(ids_records) - set(ids_params))
    to_update = df_passaporti[df_passaporti["ec5_uuid"].isin(new)]
    dict_pass = to_update.set_index('ec5_uuid')[["nome", "data_nascita"]].T.to_dict('list')
    df = pd.DataFrame.from_dict(dict_pass, orient='index', columns=["nome_cognome", "data_nascita"]).reset_index().rename(columns={"index":"ec5_uuid"})
    df = df.loc[df.nome_cognome != 38] 
    df["cognome"] = df.apply(lambda row: row.nome_cognome.split(" ")[0].lower(), axis=1)
    df["nome"] = df.apply(lambda row: row.nome_cognome.split(" ")[1:], axis=1)
    df["nome"] =  [' '.join(map(str, l)) for l in df['nome']]

    df["params"] = "raw[extra_lowercase_cognome_s] = ['" + df["nome"].str.lower() + "'] and raw[attr_nome_t] = ['" + df["cognome"] + "'] and data_nascita range ['" + df["data_nascita"].astype(str) + "-01-01 00:00\' ,  '" + df["data_nascita"].astype(str) + "-12-30 00:00\'] and "

    gc = gspread.oauth()
    sh = gc.open("params - Nati in trentino")
    worksheet_list = sh.worksheets()
    wks_id = []
    for wks in worksheet_list: 
        wks_id.append(wks.id)
    if df_params.shape[0] >= 40000:
        wks = sh.get_worksheet_by_id(wks_id[1])
    else: 
        wks = sh.get_worksheet_by_id(wks_id[0])
    wks.update([df.columns.values.tolist()] + df.values.tolist())
    print("Updated worksheet \"params - Nati in trentino\" ")
    return 


    
if __name__ == "__main__":
  update_params()   

    
