import pandas as pd
import numpy as np
import gspread

def get_data(sheet_name):
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
    df_passaporti, df_rinnovi = df_passaporti.replace("Caricamento in corso...", np.nan), df_rinnovi.replace("Caricamento in corso...", np.nan)
    df_passaporti, df_rinnovi = df_passaporti.replace("#N/A", np.nan), df_rinnovi.replace("#N/A", np.nan)
    df_passaporti, df_rinnovi = df_passaporti.dropna(how='all'), df_rinnovi.dropna(how="all")
    df_passaporti.data, df_passaporti.data_nascita, df_rinnovi.data_rinnovo = df_passaporti.data.fillna(0), df_passaporti.data_nascita.fillna(0), df_rinnovi.data_rinnovo.fillna(0)
    df_passaporti.data, df_passaporti.data_nascita, df_rinnovi.data_rinnovo = df_passaporti.data.astype(int),  df_passaporti.data_nascita.astype(int), df_rinnovi.data_rinnovo.astype(int)
    df_passaporti, df_rinnovi = df_passaporti.reset_index(), df_rinnovi.reset_index()
    return df_passaporti, df_rinnovi
    
    
def get_records_mestieri(sheet_name):
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
    df = df.replace(0, "")
    df = df.replace("", np.nan)
    df = df.replace("Caricamento in corso...", np.nan)
    df = df.replace("#N/A", np.nan)
    df = df.drop(columns="index")
    df= df.dropna(how='all')
    df.data=  df.data.fillna(0)
    df.data= df.data.astype(int)
    df.data_nascita=  df.data_nascita.fillna(0)
    df.data_nascita= df.data_nascita.astype(int)
    return df
    
def update_mestieri(): 
    df_passaporti, df_rinnovi = get_data("EpiCollect - Risposte")
    df_mestieri = get_records_mestieri("Gruppi mestieri")
    mestieri_grouped = df_mestieri.mestiere.unique()
    groups = ["Manuale","Agricolo","Commercio","Impiegatizio","Intellettuale", "Artigiano", "Sanitario", "Servitù", "Artistico","Benestante","Occasionale","Militare", "Da Rivedere", "Non Disponibile", "Clero"]
    ids_passaporti = df_passaporti.ec5_uuid.unique()
    ids_mestieri = df_mestieri.ec5_uuid.unique()
    new = list(set(ids_passaporti) - set(ids_mestieri))
    to_update = df_passaporti[df_passaporti["ec5_uuid"].isin(new)]
    mestieri = to_update.mestiere.unique()
    for el in mestieri: 
        if el in mestieri_grouped: 
            to_update.loc[to_update.mestiere == el, "Gruppo_mestiere"] = df_mestieri.loc[df_mestieri.mestiere == el, "Gruppo_mestiere"].unique()[0]
        else: 
            print(el)
            print("Scelga un gruppo tra i seguenti: ", ", ".join(groups) )
            action= input("Gruppo? ")
            if action.title() not in groups: 
                action =input("Gruppo? ")
            to_update.loc[to_update.mestiere==el, "Gruppo_mestiere"] = action.title()
    gc = gspread.oauth()
    sh = gc.open("Gruppi mestieri")
    worksheet_list = sh.worksheets()
    wks_id = []
    for wks in worksheet_list: 
        wks_id.append(wks.id)
    if df_mestieri.shape[0] >= 40000:
        wks = sh.get_worksheet_by_id(wks_id[1])
    else: 
        wks = sh.get_worksheet_by_id(wks_id[0])
    to_update = to_update.replace(np.nan, "")
    wks.update([to_update.columns.values.tolist()] + to_update.values.tolist())       
    print( "Updated Gruppi mestieri")
    return

if __name__ == "__main__":
    update_mestieri()
    
