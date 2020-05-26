import json
from typing import Dict, List, Union, Any
from docopt import docopt
from os import path
import datetime

from typing import Optional


def wrap_in_template(content: str) -> str:
    template_filepath = path.join(path.dirname(__file__), "table_template.html")
    with open(template_filepath) as file:
        template_before, template_after = (
            file.read()
            .format(today=datetime.date.today().isoformat())
            .split("<!-- CONTENT GOES HERE -->")
        )
    return template_before + content + template_after


def to_html_row(wish: Dict[str, Any], prev_wish: Optional[dict] = None) -> str:
    print('to_html_row', wish)
    try:
        return f"""
        <tr id="{wish['id']}">
            <td>{'' if prev_wish and prev_wish['name'] == wish['name'] else wish['name']}</td>
            <td>{wish['date']}</td>
            <td>{wish['ranks']['group_capacity']}</td>
            <td>{wish['ranks']['waitlist_length']}</td>
            <td>{wish['ranks']['rank']}</td>
            <td>{wish['ranks']['calllist_rank']}</td>
            <td>{wish['ranks']['max_admitted_rank']}</td>
            <td>{wish['ranks']['last_year_max_admitted_rank']}</td>
        </tr>
        """.strip()
    except KeyError as e:
        return f"""<tr><td colspan="7">
        Impossible de récupérer les données pour ce vœux.
        Vérifiez le format du JSON utilisé.
        (<code>{e}</code> manquant)</td></tr>"""


def create_table(wishes_data: Dict[str, List[Dict[str, Any]]]) -> str:
    rows_html = str()
    wishes_flat = []
    for date, wishes in wishes_data.items():
        for wish in wishes:
            print('append')
            wishes_flat.append({**wish, 'date': date})
    print('sort')
    wishes_flat = sorted(wishes_flat, key=lambda o: o['id'])
    for i, wish in enumerate(wishes_flat):
        prev_wish = wishes_flat[i-1] if i > 0 else None
        rows_html += to_html_row(wish, prev_wish)
    return wrap_in_template(rows_html)


def run(wishes_data, **cli_args):
    html = create_table(wishes_data)
    if cli_args["--out"]:
        with open(cli_args["--out"], "w") as file:
            file.write(html)
    else:
        print(html)
