# Mapping Mobilities - data curation 

Lavoro svolto da Beatrice Marsili e Maurizio Napolitano

## code 

La cartella `code` contiene tutti gli script utilizzati per la gestione della pulizia del dato

È disponibile un file requirements.txt nella cartella `code` da cui installare le librerie necessarie per performare una ricerca nel database. 
Una volta scaricata la cartella github creare un virtual environment, spostarsi nella cartella `code` e installare i requirements con `pip install -r requirements.txt`. Di sotto elencate le varie possibilità implementate.
Il primo run richiederà l'autorizzazione ad utilizzare la app Mapping Mobilities, sarà necessario effettuare il login con un account FBK. 


- Ricerca sulla base di nome e cognome con possibilità di cercare su Nati in Trentino:

```
python3 info.py cognome nome 
python3 info.py cognome nome True  # also performs a search on Nati in Trentino
```
- Visualizzazione del trend delle richieste per passaporti e rinnovi nel corso degli anni 

```
python3 historic_trend.py
```
- Visualizzazione delle destinazioni (Folium Choroplet Map): 

```
python3 plot.py continents 
python3 plot.py nations 
```

## Worflow raccolta dati
1. il data entry avviene tramite Epicollect con il progetto [Mapping Mobilities](https://five.epicollect.net/project/mapping-mobilities) secondo lo schema definito [qui](docs/Epicollect.md)
2. i dati sono raccolti in un [google sheet](https://docs.google.com/spreadsheets/d/167Mw2poD-Q9sOPe3mVtVwzEfi87Sg_rsBXxsIvrilLc/edit?usp=sharing) tramite il processo descritto [qui](docs/Epicollect.md) e lo script disponibile [qui](code/grpread_formatting.py)
3. i dati vengono visualizzati
4. i dati vengono salvati in un nuovo [google sheet](https://docs.google.com/spreadsheets/d/1WHbOewsjpBZn0QS5ceiyEoyP88p3JbQSfaZPCNA1c9U/edit?usp=sharing) con una colonna params che contiene i parametri necessari ad effettuare una ricerca su Nati in Trentino. Questo spreadsheet si può aggiornare con i nuovi dati inseriti su EpiCollect tramite la funzione `update_params`
```
python3 update_params.py
```
5. i dati vengono salvati in un [google sheet](https://docs.google.com/spreadsheets/d/1lvIOqwSLBnUlHp8sFDjPRdOaSUwq6Vx4xIE2_y4dt-k/edit?usp=sharing) con una colonna contenente i gruppi di mestieri. I mestieri e relativi gruppi sono disonibili in [questo file](https://github.com/DigitalCommonsLab/mapping_mobilities_stage/blob/70978c1b37a1778e12ead4bcbceb545c7ab17fee/code/data/mestieri.txt). Questo spreadsheet si può aggiornare con i nuovi dati inseriti su EpiCollect tramite la funzione `update_mestieri`, se i nuovi dati contengono mestieri non ancora classificati chiede input manuale.
```
python3 update_mestieri.py
```

# Scenari riuso
### Dataviz di Base 


### Integrazione con Nati in Trentino
- Nati In Trentino contiene informazioni sui dati parrocchiali dal 1815 al 1923. Il database è consultabile dal loro [sito](https://www.natitrentino.mondotrentino.net). 
- Qui si possono trovare informazioni a livello famigliare sugli individui riportati nel database, abbiamo dunque pensato potessere essere interessante provare a trovare corrispondenze tra i dati contenuti nei passaporti di emigrazione su cui questo progetto si basa e il database Nati in Trentino. 
- Abbiamo inizialmente pensato di procedere provando a ottenere tutti i dati relativi a persone nate nel periodo storico di nostro interesse (~1815-1900) con questo [script](https://github.com/DigitalCommonsLab/mapping_mobilities_stage/blob/046784fcc7a23ca8c92ee8fb946d8c8a0f3e776f/code/scraping.py).
- Abbiamo poi effettuato una ricerca mirata basandoci su NOME, COGNOME e DATA DI NASCITA delle persone di cui stiamo analizzando i passaporti utilizzando questo [codice](https://github.com/DigitalCommonsLab/mapping_mobilities_stage/blob/046784fcc7a23ca8c92ee8fb946d8c8a0f3e776f/code/match_data_natiintrentino.py).<br/> A riguardo di questo passaggio bisogna aggiungere delle considerazioni: <br/>
      1. alcuni passaporti non riportano la data di nascita, per quei casi la ricerca è stata basata semplicemente su nome e cognome;     nel dataset in cui sono salvati i dati è stata aggiunta una colonna "No data" che riporta "True" per i dati ottenuti senza basarci sulla data di nascita. Va aggiunto controllo per controllare che la data di nascita presente sul database parrocchiale sia coerente con la data di emissione del passaporto. <br/>
      2. Va ancora fatto il passaggio di controllo di corrispondenza tra comune di nascita (nostri passaporti) e parrocchia di battesimo (nati in trentino). Ci sono dei passaggi da fare prima di poter effettuare questo controllo per vari motivi. Intanto la parrocchia di battesimo potrebbe essere in un paese diverso da quello di nascita, in secondo luogo alcuni nomi sono formattati in maniera diversa per una questione temporale (es. "Bedol" / "Bedollo"). Vanno inoltre considerati eventuali errori di battitura. Una soluzione potrebbe essere utilizzare una qualche misura che cerca corrispondenze tra stringhe, abbiamo considerato la Levenshtein distance che però si basa sulla quantità di edit che necessita una stringa per diventare uguale ad un'altra stringa (es. da "Meano" a "Vigo Meano" la Levenshtein sarebbe pari a 5, che è un valore alto) e non fa al caso nostro, un'alternativa potrebbe essere la Jaccard (o Jaro-Winkler). <br/>
      3. Sarebbe intelligente assegnare a questi dati una sorta di indice di affidabilità del match (es. se nome, cognome, data di nascita, parrocchia di battesimo corrispondono esattamente con i dati in nostro possesso l'indice è pari a 1, per casi in cui il nome è diverso es. "Andreatta Narciso" vs. "Andreatta Narciso Andrea" ma data e luogo di nascita corrispondono è abbastanza probabile che si stia parlando della stessa persona, l'indice potrebbe essere pari a 0.8 e così via con valori più bassi per match potenzialmente inesatti).
- è stato realizzato un file, consultabile [qui](https://docs.google.com/spreadsheets/d/1fjT6L2lKX5Y_Ju1biyD4pgIeBlfriM6sIxMsXWUWhgM/edit?usp=sharing)(necessario account fbk) che contiene una colonna che riporta i dati di eventuali match trovati. 


### Integrazione con [Emigrazione Trentina](http://emigrazionetrentina.museostorico.it)
I passaporti che stiamo analizzando riportano dati su emigranti trentini tra fine '800 e inizio '900. Purtroppo su questi documenti non c'è un grande dettaglio relativo al luogo in cui la persona è emigrata, spesso sono infatti riportate diciture generiche come "Europa" o "America". Il centro di documentazione Emigrazione Trentina è in possesso di materiale interessante a riguardo di questo fenomeno, il loro sito è popolato da svariati elaborati, divisi per periodo storico, che riportano dati a riguardo di trentini emigrati. <br/>
Sarebbe interessante tentare di creare un modello statistico che, sulla base dei dati di Emigrazione Trentina, dell'informazione sul luogo di nascita dei migranti di cui abbiamo i passaporti, della data del loro espatrio, del riferimento generico al loro luogo di emigrazione ed eventualmente del loro mestiere, faccia una predizione sul possibile, più specifico, luogo di emigrazione. <br/> 
Citando un passaggio dell'articolo [qui](http://emigrazionetrentina.museostorico.it/la-grande-emigrazione/) disponibile "Gli spazzacamini, che partivano soprattutto dalla bassa valle di Non e dal Banale, e i segantini delle Giudicarie trovarono le migliori opportunità di lavoro nell’Italia settentrionale" provo a fare un esempio: passaporto riportante dati come "MARIO ROSSI NATO A CLES NEL 1820 SPAZZACAMINO ESPATRIATO IN ITALIA" sulla base dell'informazione sovrariportata potrebbe essere portato a un maggior grado di precisione, probabilisticamente il nostro Mario Rossi sarà plausibilmente emigrato in Italia settentrionale. 


