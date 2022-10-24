import sys
import gspread 
import pandas as pd
import requests
from pandas import json_normalize
import numpy as np
from fuzzywuzzy import fuzz


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
    df_passaporti, df_rinnovi = df_passaporti.reset_index().drop(columns="index") df_rinnovi.reset_index().drop(columns="index")
    return df_passaporti, df_rinnovi





def get_info(cognome, nome, match=False):
    '''Pass a surname and a name and obtain information regarding the person. 
    Has an additional parameter match (default=False) to perform a query on nati in trentino'''
    df_passaporti, df_rinnovi = get_records("EpiCollect - Risposte")
    input_name = cognome.lower() + " " + nome.lower()
    entry = df_passaporti[df_passaporti.nome.str.lower() == input_name]
    params = {}
    url = "https://www.natitrentino.mondotrentino.net/openpa/data/nascite"
    df_passaporti["fuzzy"] = np.nan 
    if entry.shape[0]==0: 
        print("Nessun risultato con questo nome, cerchiamo alternative simili")
        for idx, entry in df_passaporti.iterrows():
            ratio = fuzz.token_sort_ratio(input_name, entry.nome)
            df_passaporti.loc[df_passaporti.index==idx, "fuzzy"] = ratio
        entry = df_passaporti[df_passaporti.fuzzy >=83]
        if entry.shape[0] == 0: 
            res = "Nessun valore simile al nome inserito."
    if entry.shape[0] > 1: 
        indexes = entry.index.values
        print("Scelga tra i seguenti valori: ")
        for i in range(entry.shape[0]): 
            sex = entry.sesso.values[0]
            if sex == "M" or sex =="": 
                str1="nato"
            else: 
                str1="nata"
            print(i+1, ":", entry.nome.values[i], str1, "a" ,entry.luogo_nascita.values[i], "nel" ,entry.data_nascita.values[i])
        select = int(input("Inserire il numero riferito all'opzione che si vuole selezionare"))-1
        index = indexes[select]
        entry = df_passaporti[df_passaporti.index==index]
    if entry.shape[0] ==1: 
        id_entry = entry.ec5_uuid.values[0]
        luogo = entry.luogo_nascita.values[0]
        data = entry.data_nascita.values[0]
        emissione = entry.data.values[0]
        esp = entry.espatri.values[0]
        rinnovi = entry.n_rinnovi.values[0]
        validità = entry.validita.values[0]
        sex = entry.sesso.values[0]
        note = entry.note.values[0]
        mestiere = entry.mestiere.values[0]
        if sex == "M" or sex == "": 
            str1 = "nato"
            str2 = "battezzato"
            str3 = "Figlio"
        else: 
            str1 = "nata"
            str2= "battezzata"
            str3 = "Figlia"
        res = "%s %s a %s nel %s, di professione %s, ha ottenuto un passaporto nel %s con validità di %s anni con il permesso di andare in %s. " %(entry.nome.values[0], str1, luogo, data, mestiere,emissione, validità, esp )
        if note != "": 
            res+= "Note: %s" %(note)
        if rinnovi > 0: 
            entry_rinnovi = df_rinnovi[df_rinnovi.ec5_branch_owner_uuid==id_entry]
            for i in range (entry_rinnovi.shape[0]):
                data2 = entry_rinnovi.data_rinnovo.values[i]
                esp2 = entry_rinnovi.nuovi_espatri.values[i]
                note2 = entry_rinnovi.note_esp_rinnovi.values[i]
                validità2 = entry_rinnovi.validita_rinnovo.values[i]
                res += "Nel %s ottiene un rinnovo del passaporto con validità di %s anni e permesso di andare in %s. " %(data2, validità2, esp2)
                if note2 != "":
                    res += "Note: %s. " %note2
        if match:
            value = 'raw[extra_lowercase_cognome_s] = ['"%s"'] and raw[attr_nome_t] = ['"%s"'] and data_nascita range ['"%s-01-01 00:00"','"%s-12-31 00:00"'] and ' %(cognome.lower(), nome.lower() , data, data)
            params['q']=value
            data = requests.post(url, data = params)
            if "recordsTotal" in data.json() and data.json()["recordsTotal"] != 0: 
                df = json_normalize(data.json()['data'][0]['data']['ita-IT'])
                df["parrocchia_parsed"] = json_normalize(data.json()['data'][0]['data']['ita-IT'],  ['parrocchia'])['name.ita-IT'].values[0]
                df["data_nascita"] = df.data_nascita.values[0].split("T")[0]
                df = df[["cognome", "soprannome", "sesso" ,"nome", "nome_padre", "cognome_madre", "nome_madre", "data_nascita", "parrocchia_parsed"]]
                data_split = df["data_nascita"].values[0].split("-")
                data_parsed = str(data_split[2])+"-"+str(data_split[1])+"-"+str(data_split[0])
                str_match = "Trovato un potenziale match su https://www.natitrentino.mondotrentino.net: %s %s %s il %s, %s nella parrocchia di %s. %s di %s %s e %s %s." %(df.cognome.values[0], df.nome.values[0], str1,data_parsed,str2,df.parrocchia_parsed.values[0], str3, df.nome_padre.values[0], df.cognome.values[0], df.nome_madre.values[0], df.cognome_madre.values[0])
                res += str_match
            else: 
                res += "Nessun match su https://www.natitrentino.mondotrentino.net"
    print(res)
    return 



if __name__ == "__main__":
    if len(sys.argv)==3: 
        get_info(sys.argv[1], sys.argv[2])
    if len(sys.argv) ==4: 
        get_info(sys.argv[1], sys.argv[2], sys.argv[3] )  



