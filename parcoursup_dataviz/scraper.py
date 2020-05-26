from helium import *
from dotenv import load_dotenv
from os import path, getenv
from time import sleep
import re
import json
from os import makedirs
from datetime import date
from bs4 import BeautifulSoup
from pastel import colorize
from docopt import docopt


def run(**cli_args):
    args = cli_args
    parcoursup_id = None
    parcoursup_pass = None
    if args["--credentials"]:
        load_dotenv(path.expanduser(args["--credentials"]))
        parcoursup_id = getenv("PARCOURSUP_ID", None)
        parcoursup_pass = getenv("PARCOURSUP_PASS", None)
    else:
        parcoursup_id = input("N° de dossier: ")
        parcoursup_pass = input("Mot de passe: ")
    if parcoursup_id is None:
        print(
            colorize(
                '<fg=red><options=bold>ERREUR</options=bold> Veuillez préciser votre numéro de dossier (pour le fichier: PARCOURSUP_ID="Votre numéro")'
            )
        )
    if parcoursup_pass is None:
        print(
            colorize(
                '<fg=red><options=bold>ERREUR</options=bold> Veuillez préciser votre mot de passe (pour le fichier: PARCOURSUP_PASS="Votre mot de passe")'
            )
        )
    if parcoursup_id is None or parcoursup_pass is None:
        exit(1)
    # Récup le cache si présent
    cachedir = path.expanduser("~/.cache/parcoursup-dataviz")
    datadir = path.expanduser("~/.parcoursup-dataviz")
    if not path.exists(cachedir):
        makedirs(cachedir)
    yyyymmdd = date.today().isoformat()
    data_filepath = path.join(datadir, f"data.json")
    html_cache_filepath = path.join(cachedir, f"{yyyymmdd}-page.html")
    if path.exists(data_filepath):
        with open(path.join(cachedir, data_filepath), "r", encoding='utf-8') as file:
            raw = file.read() or "{}"
            wishes_data = json.loads(raw)
            wishes_data[yyyymmdd] = []
    else:
        wishes_data = {yyyymmdd: []}

    if args["--html"] and args["--in"]:
        soup = BeautifulSoup(open(args["--in"], encoding='utf-8').read(), features="lxml")
    elif path.exists(data_filepath) and not args["--no-cache"]:
        soup = BeautifulSoup(open(html_cache_filepath, encoding='utf-8').read(), features="lxml")
    else:
        browser = start_chrome(
            "https://dossierappel.parcoursup.fr/Candidat/authentification",
            headless=args["--no-browser"],
        )
        # Login
        write(parcoursup_id, into="N° de dossier")
        write(parcoursup_pass, into="Mot de passe")
        click("Connexion")
        # On attend le chargement de la page
        sleep(3)
        # On récup l'HTML de la page
        raw_html = S("body").web_element.get_attribute("innerHTML")
        # Fermer le navigateur, on en a plus besoin
        browser.close()
        # On écrit le cache
        with open(html_cache_filepath, "w", encoding='utf-8') as file:
            file.write(raw_html)
        # On parse l'HTML avec bs4
        soup = BeautifulSoup(raw_html, features="lxml")

    # On récupère les vœux
    wishes = soup.find(id="voeux_enattente").find_all("tr", class_="voeu")

    # Pour chaque vœux
    for wish in wishes:
        # Récup l'id
        wish_id = wish["id"].replace("-", "_")
        # Récup le nom
        cells = wish.find_all("td")
        wish_name = cells[2].string.strip().replace("\n", " ").replace("\t", " ")
        # Enlever les espaces dupliqués
        wish_name = re.sub(r" {2,}", " ", wish_name)
        # Récup les rangs dans la popup
        popup = soup.find("div", id=f"lst_att_{wish_id}")
        is_internat = (
            "internat" in popup.find_all("ul")[0].find_all("li")[0].contents[0]
        )
        # Initial set
        group_capacity = None
        rank = None
        waitlist_length = None
        calllist_rank = None
        max_admitted_rank = None
        last_year_max_admitted_rank = None
        internat_capacity = None
        internat_group_waitlist_rank = None
        internat_rank = None
        internat_condition_group_waitlist_rank = None
        internat_condition_rank = None
        # Traverse DOM lists
        get_number = lambda ul_idx, li_idx: int(
            popup.find_all("ul")[ul_idx]
            .find_all("li")[li_idx]
            .find("span", class_="strong")
            .string
        )
        if not is_internat:
            group_capacity = get_number(0, 0)
            rank = get_number(1, 0)
            waitlist_length = get_number(1, 1)
            calllist_rank = get_number(2, 0)
            max_admitted_rank = get_number(2, 1)
            last_year_max_admitted_rank = get_number(2, 2)
        else:
            internat_capacity = get_number(0, 0)
            internat_group_waitlist_rank = get_number(2, 0)
            internat_rank = get_number(2, 1)
            internat_situation = re.search(
                r"(?P<group>\d+)\s*ET[^\d]*(?P<rank>\d+)",
                popup.find(id="rang_cddt").find_all("p")[0].string,
            ).groupdict()
            internat_condition_group_waitlist_rank = int(internat_situation["group"])
            internat_condition_rank = int(internat_situation["rank"])

        # Add to wishes_data
        wishes_data[yyyymmdd].append(
            {
                "id": wish_id,
                "name": wish_name,
                "is_internat": is_internat,
                "ranks": {
                    "group_capacity": group_capacity,
                    "rank": rank,
                    "waitlist_length": waitlist_length,
                    "calllist_rank": calllist_rank,
                    "max_admitted_rank": max_admitted_rank,
                    "last_year_max_admitted_rank": last_year_max_admitted_rank,
                },
                "internat": {
                    "capacity": internat_capacity,
                    "group_waitlist_rank": internat_group_waitlist_rank,
                    "rank": internat_rank,
                    "condition_group_waitlist_rank": internat_condition_group_waitlist_rank,
                    "condition_rank": internat_condition_rank,
                },
            }
        )

    # Output JSON
    makedirs(path.dirname(data_filepath), exist_ok=True)
    with open(data_filepath, "w", encoding='utf-8') as file:
        file.write(json.dumps(wishes_data, indent=2))

    return wishes_data


if __name__ == "__main__":
    try:
        data = run()
        print(json.dumps(data, indent=2))
    except KeyboardInterrupt:
        print("\n\nAnnulé.")
        exit(1)
