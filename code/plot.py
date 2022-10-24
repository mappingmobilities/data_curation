import sys
import geopandas as gpd 
import folium
import pandas as pd
import numpy as np
import gspread
from IPython.display import display

def get_records(sheet_name):
    '''Pass the name of the Google Spreadsheet containing EpiCollect records
    and returns two Pandas dataframes, one for Passaporti and one for Rinnovi'''
    print("Extracting dataframes")
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
    df_passaporti, df_rinnovi = df_passaporti.dropna(how='all'), df_rinnovi.dropna(how="all")
    df_passaporti.data, df_passaporti.data_nascita, df_rinnovi.data_rinnovo = df_passaporti.data.fillna(0), df_passaporti.data_nascita.fillna(0), df_rinnovi.data_rinnovo.fillna(0)
    df_passaporti.data, df_passaporti.data_nascita, df_rinnovi.data_rinnovo = df_passaporti.data.astype(int),  df_passaporti.data_nascita.astype(int), df_rinnovi.data_rinnovo.astype(int)
    df_passaporti, df_rinnovi = df_passaporti.reset_index(), df_rinnovi.reset_index()
    return df_passaporti, df_rinnovi


def extract_dest(df, df2):
    print("Extracting destinations")
    espatri = {}
    for idx, row in df.iterrows():
        if type(row.espatri) != float:
            for el in row.espatri.split(", "): 
                if el in espatri: 
                    espatri[el] +=1 
                else: 
                    espatri[el] = 1
    for idx_rin, row_rin in df2.iterrows():
        if type(row_rin.nuovi_espatri) != float: 
            for el_rin in row_rin.nuovi_espatri.split(", "):
                if el_rin in espatri: 
                    espatri[el_rin]+=1
                else: 
                    espatri[el_rin] = 1 
    return espatri


def destinations_continents(): 
    """Creates a .html file that has to be manually opened to show the Choroplet map representing the destinations as continents"""
    df_passaporti, df_rinnovi = get_records("EpiCollect - Risposte")
    espatri = extract_dest(df_passaporti, df_rinnovi)
    espatri_continenti = espatri.copy()
    espatri_continenti["Europe"] = espatri_continenti.pop("Europa")
    espatri_continenti["Europe"] += espatri_continenti.pop("Germania")
    espatri_continenti["Europe"] += espatri_continenti.pop("Italia")
    espatri_continenti["Europe"] += espatri_continenti.pop("Austria")
    espatri_continenti["Europe"] += espatri_continenti.pop("Francia")
    espatri_continenti["Europe"] += espatri_continenti.pop("Svizzera")
    espatri_continenti["Europe"] += espatri_continenti.pop("Austria-Ungheria")
    espatri_continenti["Europe"] += espatri_continenti.pop("Ungheria")
    espatri_continenti["Europe"] += espatri_continenti.pop("Esteri d'Europa")
    espatri_continenti["Europe"] += espatri_continenti.pop("Turchia")
    espatri_continenti["Europe"] += espatri_continenti.pop("Bosnia-Erzegovina")
    world_all = gpd.read_file("data/WB_countries_Admin0_10m/WB_countries_Admin0_10m.shp")
    world = world_all.dissolve(by="CONTINENT").reset_index()[["CONTINENT", "geometry"]]
    america = world.loc[(world.CONTINENT=="North America") | (world.CONTINENT=="South America")].dissolve()
    america = america[["geometry", "CONTINENT"]]
    america = america.replace("North America", "America")
    world = world.loc[(world["CONTINENT"] != "North America") & (world["CONTINENT"] != "South America")]
    world = world.append(america)
    world = world.to_crs("epsg:4326")
    au_empire_1910 = gpd.read_file("data/Austro-Hungarian Empire 1910/Austro_Hungarian_Empire_1910_v.1.0.shp")
    au_empire_1910 = au_empire_1910.to_crs("epsg:4326")
    tirolo_1910 = au_empire_1910.loc[au_empire_1910.LAND=="TIROL"]
    tirolo_1910 = tirolo_1910.dissolve()
    tirolo_1910 = tirolo_1910[["geometry", "LAND"]]
    tirolo_poly = tirolo_1910.geometry.values[0]
    world.loc[world.CONTINENT=="Europe", "geometry"] = world.loc[world.CONTINENT=="Europe"].geometry.difference(tirolo_poly)
    world["Num"] = world["CONTINENT"].map(espatri_continenti)
    world["Num"] = world["Num"].fillna(0)
    world["Num"] = world["Num"].astype(int)
    m = folium.Map(zoom_start=5, 
                    location=[-23, -46])
    folium.Choropleth(
        geo_data=world,
        name="choropleth",
        data=world,
        columns=["CONTINENT", "Num"],
        key_on = 'feature.properties.CONTINENT',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Espatri",
        nan_fill_color='white',
        fill_color="PuRd"
    ).add_to(m)
    for geom, name, num in zip(world.geometry, world.CONTINENT, world.Num):
        if name != "Seven seas (open ocean)":
            lat, lon = geom.centroid.y, geom.centroid.x
            folium.Marker(
            location=[lat, lon],
            popup=str(name)+ ": " + str(int(num))
            ).add_to(m)
    m.save("continents.html")
    print("HTML of the map saved and ready to be manually opened")
    return display(m)


def destinations_nations(): 
    df_passaporti, df_rinnovi = get_records("EpiCollect - Risposte")
    espatri = extract_dest(df_passaporti, df_rinnovi)    
    espatri_nazioni = espatri.copy()
    espatri_nazioni["Austria-Ungheria"] += espatri_nazioni.pop("Austria")
    espatri_nazioni["Austria-Ungheria"] += espatri_nazioni.pop("Ungheria")
    espatri_nazioni.pop("Europa")
    espatri_nazioni.pop("America")
    espatri_nazioni.pop("Esteri d'Europa")
    espatri_nazioni.pop("Asia")
    espatri_nazioni.pop("Africa")
    espatri_nazioni["Germany"] = espatri_nazioni.pop("Germania")
    espatri_nazioni["France"] = espatri_nazioni.pop("Francia")
    espatri_nazioni["Switzerland"] = espatri_nazioni.pop("Svizzera")
    espatri_nazioni["Austria Hungary"] = espatri_nazioni.pop("Austria-Ungheria")
    espatri_nazioni["Ottoman Empire"] = espatri_nazioni.pop("Turchia")
    espatri_nazioni["Bosnia-Herzegovina"] = espatri_nazioni.pop("Bosnia-Erzegovina")
    espatri_nazioni["Italy"] = espatri_nazioni.pop("Italia")
    au_empire_1910 = gpd.read_file("data/Austro-Hungarian Empire 1910/Austro_Hungarian_Empire_1910_v.1.0.shp")
    au_empire_1910 = au_empire_1910.to_crs("epsg:4326")
    tirolo_1910 = au_empire_1910.loc[au_empire_1910.LAND=="TIROL"]
    tirolo_1910 = tirolo_1910.dissolve()
    tirolo_1910 = tirolo_1910[["geometry", "LAND"]]
    tirolo_poly = tirolo_1910.geometry.values[0]
    nazioni = gpd.read_file("data/nations_1880/cntry1880.shp")
    nazioni = nazioni.dissolve(by="NAME").reset_index()
    nazioni = nazioni.set_crs("epsg:4326")
    nazioni = nazioni[["NAME", "geometry"]]
    nazioni.loc[nazioni.NAME=="Austria Hungary", "geometry"]= nazioni.loc[nazioni.NAME=="Austria Hungary"].geometry.difference(tirolo_poly)
    nazioni.loc[nazioni.NAME=="Switzerland", "geometry"]= nazioni.loc[nazioni.NAME=="Switzerland"].geometry.difference(tirolo_poly)
    nazioni.loc[nazioni.NAME=="Lombardy", "geometry"]= nazioni.loc[nazioni.NAME=="Lombardy"].geometry.difference(tirolo_poly)
    nazioni.loc[nazioni.NAME=="Germany", "geometry"]= nazioni.loc[nazioni.NAME=="Germany"].geometry.difference(tirolo_poly)
    nazioni.loc[nazioni.NAME=="Lombardy", "NAME"]= "Italy"
    nazioni["Num"] = nazioni["NAME"].map(espatri_nazioni)
    nazioni.Num = nazioni.Num.fillna(0)
    nazioni.Num = nazioni.Num.astype(int)
    location = (nazioni.loc[nazioni.NAME=="Italy"].centroid.y.values[0], nazioni.loc[nazioni.NAME=="Italy"].centroid.x.values[0])
    m = folium.Map(zoom_start=4, location = location)
    folium.Choropleth(
        geo_data=nazioni,
        name="nazioni",
        data=nazioni,
        columns=["NAME", "Num"],
        key_on = 'feature.properties.NAME',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Espatri",
        nan_fill_color='white',
        fill_color="PuRd"
    ).add_to(m)
    for geom, name, num in zip(nazioni.geometry, nazioni.NAME, nazioni.Num):
        if num > 0:
            lat, lon = geom.centroid.y, geom.centroid.x
            folium.Marker(
            location=[lat, lon],
            popup=str(name)+ ": " + str(int(num))
            ).add_to(m)
    m.save("nations.html")
    print("HTML of the map saved and ready to be manually opened")
    return display(m)
    





if __name__ == "__main__":
    if sys.argv[1] == "continents":
        destinations_continents()
    if sys.argv[1] =="nations": 
        destinations_nations()
    if sys.argv[1] != "continents" and sys.argv[1] != "nations": 
        raise ValueError("plot.py possible arguments: continents or nations.")
