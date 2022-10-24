import pandas as pd 
import requests
from pandas import json_normalize

def match_data(passports, path):
  '''Takes a CSV file with passport data and a path to a Google drive folder, tries to match entries of the dataframe with data in "Nati in Trentino" database.
  If there is a match (at least with name + surname) the corresponding data is saved in the Google Drive folder provided on the call of the function.'''
  if type(passports)!= pd.core.frame.DataFrame: 
    raise ValueError ("Please pass a valid Pandas DataFrame")
  params = {}
  url = "https://www.natitrentino.mondotrentino.net/openpa/data/nascite"
  for idx, entry in passports.iterrows(): 
    cognome = entry.nome.split(" ")[0].lower()
    nome = ' '.join([str(elem) for elem in entry.nome.split(" ")[1:]]).lower()
    if entry.data_nascita != 0:
      value = 'raw[extra_lowercase_cognome_s] = ['"%s"'] and raw[attr_nome_t] = ['"%s"'] and data_nascita range ['"%s-01-01 00:00"','"%s-12-30 00:00"'] and ' %(cognome, nome , entry.data_nascita, entry.data_nascita)
    else:
      value = 'raw[extra_lowercase_cognome_s] = ['"%s"'] and raw[attr_nome_t] = ['"%s"'] and data_nascita range ['"1800-01-01 00:00"','"1900-12-30 00:00"'] and ' %(cognome, nome)
    params['q']=value
    data = requests.post(url, data = params)
    if data.json()["recordsTotal"] != 0 : 
        df = json_normalize(data.json()['data'][0]['data']['ita-IT'])
        df['parrocchia_parsed'] = json_normalize(data.json()['data'][0]['data']['ita-IT'],  ['parrocchia'])['name.ita-IT'].values[0]
        df['comune_parsed'] = json_normalize(data.json()['data'][0]['data']['ita-IT'],  ['comune'])['name.ita-IT'].values[0]
        df['comunita_parsed'] = json_normalize(data.json()['data'][0]['data']['ita-IT'],  ['comunita'])['name.ita-IT'].values[0]
        if entry.data_nascita == 0:
          df['no_data'] = True
        else: 
          df['no_data'] = False
        df.to_csv("%s/match_%s_%s_%s.csv" %(path, cognome, nome, idx), index=False)
  return 



import os 
def merge_all_match (path):
  '''Takes the path to a Google drive folder where the function "match_data" has been called on, merges the files 
  in the folder which name starts with "match" (as saved by match_data function) into a new dataframe "match.csv".'''
  i = 0 
  for entry in os.scandir(path):  
    if entry.name.startswith("match"):
      if i == 0:
        df = pd.read_csv(entry)
        i+=1
      else: 
        new_df = pd.read_csv(entry)
        df = df.append(new_df)
  return df.to_csv("%s/match.csv", %s(path) index=False)
