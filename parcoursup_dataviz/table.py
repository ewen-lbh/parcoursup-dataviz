import json
from typing import Dict, List, Union
from docopt import docopt


FANCY_COLUMN_NAMES = {
    "id": "ID",
    "name": "Nom",
    "ranks": {
        "group_capacity": "Capacité du groupe",
        "rank": "Position dans la file d'attente",
        "waitlist_length": "Taille de la file d'attente",
        "group_rank": "Position dans la fiche d'appel",
        "max_admitted_rank": "",
        "last_year_max_admitted_rank": "",
    },
    "internat": {
        "capacity": "",
        "group_waitlist_rank": "",
        "rank": "",
        "condition_group_waitlist_rank": "",
        "condition_rank": "",
    },
}


def structuralize(wishes_data: Dict[str, Union[str, dict, bool, int]]) -> List[List[str]]:
    

# def make_html_table(wishes_data: Dict[str, Union[int, dict, bool, str]]) -> str:
    
