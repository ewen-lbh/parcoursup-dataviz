from helium import *
from dotenv import load_dotenv
from os import path, getenv
from time import sleep
import re
from os import makedirs
from bs4 import BeautifulSoup
from pastel import colorize
from docopt import docopt

def run():
    load_dotenv(path.expanduser('~/.parcoursup_creds'))

    args = docopt("""Usage: automation_parcoursup.py [options]

    --cache  Use the cache (in ~/.cache/automation-parcoursup/admission.html)
    """)

    # Récup le cache si présent
    cachedir = path.expanduser('~/.cache/automation-parcoursup')
    if not path.exists(cachedir):
        makedirs(cachedir)
    cachefile = path.join(cachedir, 'admission.html')
    if path.exists(cachefile) and args['--cache']:
        soup = BeautifulSoup(open(cachefile).read(), features='lxml')
    else:
        browser = start_firefox('https://dossierappel.parcoursup.fr/Candidat/authentification')
        # Login
        write(getenv('PARCOURSUP_ID'), into='N° de dossier')
        write(getenv('PARCOURSUP_PASS'), into='Mot de passe')
        click('Connexion')
        # On attend le chargement de la page
        sleep(3)
        # On récup l'HTML de la page
        raw_html = S('body').web_element.get_attribute('innerHTML')
        # Fermer le navigateur, on en a plus besoin
        browser.close()
        # On écrit le cache
        with open(cachefile, 'w') as file:
            file.write(raw_html)
        print('Written response to cache.')
        # On parse l'HTML avec bs4
        soup = BeautifulSoup(raw_html, features='lxml')


    # On récupère les vœux
    wishes = soup.find(id='voeux_enattente').find_all('tr', class_='voeu')

    # Pour chaque vœux
    for wish in wishes:
        # Récup l'id
        wish_id = wish['id'].replace('-', '_')
        # Récup le nom
        cells = wish.find_all('td')
        wish_name = cells[2].string.strip().replace('\n', ' ').replace('\t', ' ')
        # Enlever les espaces dupliqués
        wish_name = re.sub(r' {2,}', ' ', wish_name)
        # Récup les rangs dans la popup
        popup = soup.find('div', id=f'lst_att_{wish_id}').find(id='rang_cddt')
        try:
            rank = int(popup.find_all('ul')[0].find_all('li')[0].find('span', class_='strong').string)
            last_year_max_rank = int(popup.find_all('ul')[1].find_all('li')[2].find('span', class_='strong').string)
        
        except IndexError:
            print(colorize(f'<options=bold>Vœu:</> <options=dark>{wish_name}</>'))
            print('\t(Internat)')
        else:
            diff_abs = last_year_max_rank - rank
            diff_rel = diff_abs / last_year_max_rank
            color = 'green' if diff_abs >= 0 else 'red'
            print(colorize(f'<options=bold;fg={color}>Vœu:</> <options=dark>{wish_name}</>'))
            print(colorize(f'\tYours         <options=dark>#</><options=bold>{rank}</>'))
            print(colorize(f'\tMax last year <options=dark>#</><options=bold>{last_year_max_rank}</>'))
            print(colorize(f'\tDelta:      <options=dark>rel: </><options=bold>{diff_rel*100:.1f}</><options=dark>%</>'))
            print(colorize(f'\t            <options=dark>abs: </><options=bold>{diff_abs}</>'))
        print('')
        # ranks_sel = f'#lst_att_{wish_id} #rang_cddt '
        # position = S(ranks_sel + '> ul:first-child > li:first-child > span.strong').web_element.text
