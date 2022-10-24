import pandas as pd
import gspread 
import numpy as np
import matplotlib.pyplot as plt 


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
    df_passaporti, df_rinnovi = df_passaporti.replace("#N/A", np.nan), df_rinnovi.replace("#N/A", np.nan)
    df_passaporti, df_rinnovi = df_passaporti.replace("Caricamento in corso...", np.nan), df_rinnovi.replace("Caricamento in corso...", np.nan)
    df_passaporti, df_rinnovi = df_passaporti.dropna(how='all'), df_rinnovi.dropna(how="all")
    df_passaporti.data, df_passaporti.data_nascita, df_rinnovi.data_rinnovo = df_passaporti.data.fillna(0), df_passaporti.data_nascita.fillna(0), df_rinnovi.data_rinnovo.fillna(0)
    df_passaporti.data, df_passaporti.data_nascita, df_rinnovi.data_rinnovo = df_passaporti.data.astype(int),  df_passaporti.data_nascita.astype(int), df_rinnovi.data_rinnovo.astype(int)
    df_passaporti, df_rinnovi = df_passaporti.reset_index(), df_rinnovi.reset_index()
    return df_passaporti, df_rinnovi

def plot_data():
    df_passaporti, df_rinnovi = get_data("EpiCollect - Risposte")
    df_analysis = df_passaporti[df_passaporti.data != 0]
    df_analysis2 = df_rinnovi[df_rinnovi.data_rinnovo != 0]
    grouped = df_analysis.groupby(["data"]).size().to_frame("num").sort_values(["data"], ascending=True).reset_index()
    grouped_rinnovi = df_analysis2.groupby(["data_rinnovo"]).size().to_frame("num").sort_values(["data_rinnovo"], ascending=True).reset_index()
    grouped_rinnovi=grouped_rinnovi.rename(columns={"data_rinnovo":"data"})
    all_grouped = pd.merge(grouped, grouped_rinnovi, on="data", how="outer")
    all_grouped = all_grouped.fillna(0)
    all_grouped.num_x = all_grouped.num_x.astype(int)
    all_grouped.num_y = all_grouped.num_y.astype(int)
    all_grouped["total"] = all_grouped.num_x + all_grouped.num_y
    ylim = max(all_grouped.total) + 30
    data1 = all_grouped.num_x.tolist()
    data2 = all_grouped.num_y.tolist()
    bars = all_grouped.data.tolist()
    y_pos = np.arange(len(bars))
    plt.rcParams["figure.figsize"] = [15, 7]
    plt.rcParams["figure.autolayout"] = True
    plt.bar(range(len(data1)), data1, label="Passaporti", color=["#E7B800"])
    plt.bar(range(len(data2)), data2, bottom=data1, label="Rinnovi", color= ["#006060"])
    plt.xticks(np.arange(len(bars), step=1), bars, rotation=45)
    plt.title("Andamento delle richieste totali negli anni", fontsize=20, ha="center")
    plt.legend(["Passaporti", "Rinnovi"])
    return plt.show()


if __name__ == "__main__":
    plot_data()
