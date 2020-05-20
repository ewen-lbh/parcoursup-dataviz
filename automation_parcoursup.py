from helium import *
from dotenv import load_dotenv
from os import path, getenv
from time import sleep
import re
load_dotenv(path.join(path.dirname(__file__), '.parcoursup_creds'))

browser = start_firefox('https://dossierappel.parcoursup.fr/Candidat/authentification')

try:
    # Login
    write(getenv('PARCOURSUP_ID'), into='N° de dossier')
    write(getenv('PARCOURSUP_PASS'), into='Mot de passe')
    click('Connexion')

    # Récup l'HTML
    sleep(10)
    raw_html = S('body').web_element.get_attribute('innerHTML')
    
    # wishes = find_all(S('#voeux_enattente tr'))
    # print(wishes)
    # # Pour chaque vœux
    # for wish in wishes:
    #     continue
    #     # Récup l'id
    #     wish_id = wish.web_element.get_attribute('id').replace('-', '_')
    #     # Récup le nom
    #     print(dir(wish.web_element))
    #     wish_name = wish.web_element.find_element('td:nth-child(3)')
    #     print(f'Vœu: {wish_name}')
    #     # Récup la popup
    #     ranks_sel = f'#lst_att_{wish_id} #rang_cddt '
    #     position = S(ranks_sel + '> ul:first-child > li:first-child > span.strong').web_element.text
        
    
finally:
    browser.close()
