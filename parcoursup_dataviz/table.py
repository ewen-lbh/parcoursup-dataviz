import json
from typing import Dict, List, Union, Any
from docopt import docopt
from os import path
import datetime

from typing import Optional


def wrap_in_template(content: str) -> str:
    template_filepath = path.join(path.dirname(__file__), "table_template.html")
    with open(template_filepath, encoding='utf-8') as file:
        template_before, template_after = (
            file.read()
            .replace('{today}', datetime.date.today().strftime('%d %B %Y'))
            .split("<!-- CONTENT GOES HERE -->")
        )
    return template_before + content + template_after


def to_html_row(wish: Dict[str, Any], same_wish: bool = False) -> str:
    try:
        static_value = lambda x: '' if same_wish else x
        fmt_date = datetime.datetime.strptime(wish['date'], '%Y-%m-%d').strftime('%b %d')
        return f"""
        <tr {'class="new-wish"' if not same_wish else ''}>
            <td class="static">{static_value(wish['name'])}</td>
            <td class="static">{static_value(str(wish['ranks']['group_capacity']).replace('None', '<i>N/A</i>'))}</td>
            <td>{fmt_date}</td>
            <td>{str(wish['ranks']['waitlist_length']).replace('None', '<i>N/A</i>')}</td>
            <td>{str(wish['ranks']['rank']).replace('None', '<i>N/A</i>')}</td>
            <td class="static">{static_value(str(wish['ranks']['calllist_rank']).replace('None', '<i>N/A</i>'))}</td>
            <td>{str(wish['ranks']['max_admitted_rank']).replace('None', '<i>N/A</i>')}</td>
            <td class="static">{static_value(str(wish['ranks']['last_year_max_admitted_rank']).replace('None', '<i>N/A</i>'))}</td>
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
            wishes_flat.append({**wish, 'date': date})
    wishes_flat = sorted(wishes_flat, key=lambda o: o['id'])
    for i, wish in enumerate(wishes_flat):
        prev_wish = wishes_flat[i-1] if i > 0 else None
        same_wish = bool(prev_wish and prev_wish['name'] == wish['name'])
        rows_html += to_html_row(wish, same_wish)
    return wrap_in_template(rows_html)


def run(wishes_data, **cli_args):
    html = create_table(wishes_data)
    if cli_args["--out"]:
        with open(cli_args["--out"], "w", encoding='utf-8') as file:
            file.write(html)
    else:
        print(html)
