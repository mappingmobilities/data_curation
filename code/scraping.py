import requests
import urllib.parse
from pandas import json_normalize
import os 

def start_value(path):
  data = [int(entry.name[3:-4]) for entry in os.scandir(path) if entry.name.startswith("df_")]
  start = max(data)
  return start+100
  
def max_value(url):
  value = 'sesso = [\'F\',\'M\'] and data_nascite range[\'1800-01-01 00:00\',\'1900-12-31 00:00\']'
  params= {}
  params['q'] = value   
  params["length"] = 1 
  data = requests.post(url, data = params)
  max = data.json()["recordsTotal"]
  return max 

def scrape_all(url): 
  params= {}
  value = 'sesso = [\'F\',\'M\'] and data_nascite range[\'1800-01-01 00:00\',\'1900-12-31 00:00\']'
  params['q'] = value
  params["start"] = start_value("/content/drive/MyDrive/Colab Notebooks/Data_tirocinio")
  params["length"] = max_value("https://www.natitrentino.mondotrentino.net/openpa/data/nascite")
  i = params["start"]
  while params["start"] <= params["length"]: 
    data = requests.post(url, data = params)
    df = json_normalize(data.json()["data"])
    df.to_csv("/content/drive/MyDrive/Colab Notebooks/Data_tirocinio/df_%s.csv" %(i))
    params["start"] += 100
    i += 100 
  return  
  
scrape_all("https://www.natitrentino.mondotrentino.net/openpa/data/nascite")    
   
def merge_all (path):
  i = 0 
  for entry in os.scandir(path):  
    if entry.name.startswith("df"):
      if i == 0:
        df = pd.read_csv(entry)
        i+=1
      else: 
        new_df = pd.read_csv(entry)
        df = df.append(new_df)
  return df.to_csv("/content/drive/MyDrive/Colab Notebooks/Data_tirocinio/total.csv")
  
 merge_all("/content/drive/MyDrive/Colab Notebooks/Data_tirocinio") 
  
  
 
