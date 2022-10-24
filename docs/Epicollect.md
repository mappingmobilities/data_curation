## Mapping Data
#### Informazioni Passaporto
- Numero Busta -> per identificare data collector
- Nome e Cognome 
- Data Nascita 
- Luogo Nascita 
- Sesso 
- Lavoro di origine 
- Lavoro nel paese di destinazione
- Data emissione passaporto 
- Validità passaporto 

#### Informazioni Espatri 
- Nazioni di espatrio 

#### Informazioni Rinnovi
- Data Rinnovo 
- Validità Rinnovo 
- Nazioni di espatrio nei rinnovi 

#### Difficoltà interpretazione 
- Campi in cui c'è stata difficoltà nel comprendere la scrittura manuale 
- Ulteriori informazioni contenute nel passaporto 
- Eventuale foto del passaporto

## Workflow 
<img src="https://github.com/DigitalCommonsLab/mapping_mobilities_stage/blob/13aec32502adbeed6c50fd4aa0e54eb7dfbf40bc/images/screenshots/Epi%20collect.png" height="350" width="800">

## Form structure 
<img src=https://github.com/DigitalCommonsLab/mapping_mobilities_stage/blob/a191277c59b3b34f95ab92f0354b51bd05214505/images/screenshots/Form.png>

## Google Sheet 
Utilizzando le API fornite da EpiCollect5 i dati sono importabili in un file GoogleSheet con la funzione IMPORTDATA.
Il progetto è composto da due branch: quello dedicato alle informazioni del primo passaporto e quello dedicato ai rinnovi, abbiamo dunque due diverse chiavi API che produrranno di conseguenza due differenti worksheet. 
- API Passaporti: https://five.epicollect.net/api/export/entries/mapping-mobilities?form_ref=a58c54c21f76430c90739297c520f882_605defdd4059f
- API Rinnovi: https://five.epicollect.net/api/export/entries/mapping-mobilities?form_ref=a58c54c21f76430c90739297c520f882_605defdd4059f&branch_ref=a58c54c21f76430c90739297c520f882_605defdd4059f_606c9d420f775 <br/>


Ogni formula IMPORTDATA supporta l'importazione di 1000 entries, ogni worksheet supporta l'inserimento di 50 formule IMPORTDATA. 
Dobbiamo digitalizzare 60.000 passaporti, non sappiamo quanti di questi siano primi passaporti e quanti siano rinnovi, ho dunque considerato il caso limite in cui abbiamo 60.000 righe in passaporti e 60.000 in rinnovi. Per i limiti relativi alle formule IMPORTDATA avremo quindi bisogno di due worksheet per i Passaporti e due per i Rinnovi. In questi worksheet devono esserci: 
1. nella prima riga del primo worksheet la formula IMPORTDATA con header e pagina = 1 
2. ogni 1000 righe la formula IMPORTDATA senza header e pagina progressiva (es. 2, 3, 4, etc.) fino all'inserimento di 40.000 righe 
3. nella prima riga del secondo worksheet avremo di nuovo bisogno di inserire IMPORTDATA con header e ancora pagine progressive 
4. ogni 1000 righe la formula IMPORTDATA senza header e pagina progressiva fino all'inserimento di 20.000 righe <br/>

Il processo va ovviamente ripetuto per ambedue le API. 

## Gspread 
É stato realizzato uno script in Python utilizzando la libreria `gspread` e appoggiandoci a una App in Google Cloud Platform per gestire questo processo in automatico. Lo script crea un nuovo Foglio di Google, cancella il primo worksheet creato automaticamente (Foglio1), ne crea due nuovi (uno per passaporti e uno per rinnovi), formatta lo stile della prima riga e la blocca, inizia l'inserimento della formula IMPORTDATA come spiegato nel paragrafo precedente. Al raggiungimento delle 40.000 entrate crea due nuovi worksheet e continua con l'inserimento delle formule IMPORTDATA per ambedue i nuovi fogli di lavoro. Per rispettare i limiti delle API di Google su cui si appoggia la libreria `gspread` lo script ha delle pause di 1 minuto dopo un certo numero di azioni; l'intero processo impiega circa 5 minuti e rientra nel limite gratuito delle chiamate alle Google API.
Lo script è disponibile [qui](https://github.com/DigitalCommonsLab/mapping_mobilities_stage/blob/main/code/grpread_formatting.py).

## Mapping Data Collectors 
Abbiamo ragionato su quale fosse il miglior modo per risalire a chi ha inserito ogni entry nel sistema di EpiCollect5, tentando di evitare di aggiungere un passaggio manuale ma non è stato possibile. <br/>
EpiCollect5, infatti, riporta le iniziali del collector e/o la sua mail nel dataset finale solamente per i progetti privati. Settando la visibilità del progetto a "privato" sarebbe però impossibile utilizzare le API e importare i dati in GoogleSheet. <br/>
Abbiamo dunque deciso di inserire nel form il campo "numero busta". Chiederemo ai collaboratori del museo storico di condividere con noi una tabella che elenchi i data collector e le buste loro assegnate, in modo tale da poter rislire facilmente al collector di ogni valore nel dataset. 
