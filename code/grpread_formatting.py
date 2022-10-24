
import string
import gspread
gc = gspread.oauth()                                #works with an app on Google Cloud Platform
from gspread_formatting import set_frozen
import time

def create_google_sheet(user_email):
    loop=0
    cell_counter = 1
    pagina = 1
    inserted = 0
    sh = gc.create('Database risposte')                                     #Google Spreadsheet creation
    format_header={"backgroundColor": {                                     #header formatting definition
                                  "red": 0.3,
                                  "green": 0.1,
                                  "blue": 0.8},
                   "horizontalAlignment": "CENTER",
                    "textFormat": {
                    "foregroundColor": {
                                    "red": 0.9,
                                    "green": 0.8,
                                    "blue": 0},
                    "fontSize": 10,
                    "bold": True}}
    while inserted <60000:
        loop+=1
        if pagina == 1 :                                                                        
            sh.add_worksheet(title='Database risposte Personali1', rows='40000', cols='19')     #adds Worksheet for personal responses 
            sh.del_worksheet(sh.get_worksheet(0))                                               #deletes initial automatic worksheet 
            worksheet_counter = 1
            alpha = list(string.ascii_uppercase)
            header_personali = "A1:%s1" %alpha[19]
            sh.worksheet('Database risposte Personali%s'%worksheet_counter).format(header_personali, format_header) #formats the header
            set_frozen(sh.worksheet('Database risposte Personali%s' %worksheet_counter), rows= 1)                   #blocks first row
            set_frozen(sh.worksheet('Database risposte Personali%s' %worksheet_counter), cols= 1)                   #blocks first column (with ec5_uuid)
            sh.share(user_email, perm_type='user', role='writer')
            formula_personali = '=IMPORTDATA("https://five.epicollect.net/api/export/entries/mapping-mobilities?form_ref=a58c54c21f76430c90739297c520f882_605defdd4059f&format=csv&per_page=1000&page=%s")' %pagina  #formula with header for personal responses 
            cell = "A%s" % cell_counter
            sh.worksheet('Database risposte Personali%s'%worksheet_counter).update(cell, formula_personali, value_input_option='USER_ENTERED')  #inserts the first IMPORTDATA for personal responses
            time.sleep(60)
            sh.add_worksheet(title='Database risposte Rinnovi%s'%worksheet_counter, rows='40000', cols='9')
            header_rinnovi = "A1:%s1" %alpha[8]
            sh.worksheet('Database risposte Rinnovi%s'%worksheet_counter).format(header_rinnovi, format_header)
            set_frozen(sh.worksheet('Database risposte Rinnovi%s'%worksheet_counter), rows= 1)
            set_frozen(sh.worksheet('Database risposte Rinnovi%s'%worksheet_counter), cols= 1)            
            formula_rinnovi = '=IMPORTDATA("https://five.epicollect.net/api/export/entries/mapping-mobilities?form_ref=a58c54c21f76430c90739297c520f882_605defdd4059f&branch_ref=a58c54c21f76430c90739297c520f882_605defdd4059f_606c9d420f775&format=csv&per_page=1000&page=%s")'%pagina #formula with header for renewal responses 
            sh.worksheet('Database risposte Rinnovi%s'%worksheet_counter).update(cell, formula_rinnovi, value_input_option='USER_ENTERED')    #inserts the first IMPORTDATA for renewal responses
            inserted +=1000
            pagina += 1
            cell_counter = 1002
            time.sleep(60)              #60 seconds of stop
        if pagina == 40:
            worksheet_counter +=1
            sh.add_worksheet(title='Database risposte Personali%s' %worksheet_counter, rows='21000', cols='19')         #reached the limit per worksheet, creates a new worksheet for personal responses
            sh.worksheet('Database risposte Personali%s'%worksheet_counter).format(header_personali, format_header)      #formats the header
            set_frozen(sh.worksheet('Database risposte Personali%s' %worksheet_counter), rows= 1)                   #blocks first row
            set_frozen(sh.worksheet('Database risposte Personali%s' %worksheet_counter), cols= 1)                   #blocks first column (with ec5_uuid)
            cell_counter = 1
            formula_personali = '=IMPORTDATA("https://five.epicollect.net/api/export/entries/mapping-mobilities?form_ref=a58c54c21f76430c90739297c520f882_605defdd4059f&format=csv&per_page=1000&page=%s")' %pagina         #again formula with header for the new worksheet 
            cell = 'A%s' %cell_counter
            sh.worksheet('Database risposte Personali%s' %worksheet_counter).update(cell, formula_personali, value_input_option='USER_ENTERED')                 #inserts first IMPORTDATA of second worksheet
            sh.add_worksheet(title='Database risposte Rinnovi%s' %worksheet_counter, rows='21000', cols='9')                                            #repeats the process for renewal responses
            sh.worksheet('Database risposte Rinnovi%s' %worksheet_counter).format(header_rinnovi, format_header)
            set_frozen(sh.worksheet('Database risposte Rinnovi%s' %worksheet_counter), rows= 1)
            set_frozen(sh.worksheet('Database risposte Rinnovi%s' %worksheet_counter), cols= 1) 
            formula_rinnovi = '=IMPORTDATA("https://five.epicollect.net/api/export/entries/mapping-mobilities?form_ref=a58c54c21f76430c90739297c520f882_605defdd4059f&branch_ref=a58c54c21f76430c90739297c520f882_605defdd4059f_606c9d420f775&format=csv&per_page=1000&page=%s")'%pagina
            sh.worksheet('Database risposte Rinnovi%s' %worksheet_counter).update(cell, formula_rinnovi, value_input_option='USER_ENTERED')            
            cell_counter= 1002
            pagina +=1
            inserted +=1000
            time.sleep(60)                      #sleeps for 60 seconds before starting inserting new formulas 
        else:                                   #here the process is much simpler: once every 1000 rows it is inserted an IMPORTDATA formula for both the worksheets.
            cell = 'A%s' %cell_counter
            formula_personali = '=IMPORTDATA("https://five.epicollect.net/api/export/entries/mapping-mobilities?form_ref=a58c54c21f76430c90739297c520f882_605defdd4059f&format=csv&per_page=1000&page=%s&headers=false")' %pagina            
            sh.worksheet('Database risposte Personali%s' %worksheet_counter).update(cell, formula_personali, value_input_option='USER_ENTERED')
            formula_rinnovi = '=IMPORTDATA("https://five.epicollect.net/api/export/entries/mapping-mobilities?form_ref=a58c54c21f76430c90739297c520f882_605defdd4059f&branch_ref=a58c54c21f76430c90739297c520f882_605defdd4059f_606c9d420f775&format=csv&per_page=1000&page=%s&headers=false")'%pagina
            sh.worksheet('Database risposte Rinnovi%s' %worksheet_counter).update(cell, formula_rinnovi, value_input_option='USER_ENTERED')
            cell_counter +=1000            
            pagina +=1
            inserted +=1000
        if loop%20==0: 
            time.sleep(60)                      #sleeps 60 seconds once every 20 loops
    return 


create_google_sheet("insert here the email of the user that needs writer permissions. the user has to be authorized on the App on google cloud platform")
        
