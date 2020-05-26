"""Scrapes parcoursup.fr and generates graphs for each wish in the waitlist. 
See https://github.com/ewen-lbh/parcoursup-dataviz for more information.

Usage: parcoursup-dataviz [options]

Arguments:
    --in=FILE               Input file. Opens an automated browser to get the HTML 
                            or uses the cache if not given. If --html isn't present, 
                            the input file is assumed to be a JSON file with 
                            the same structure as the one used internall 
                            (refer to the README.md)

    --out=FILE              Output file. If --json is used, not specifying this will
                            print the JSON to stdin.
                            Without --json, if --out is omitted, a default filename
                            will be used.

Options:
    --no-cache              Deactivates the cache

    -B --no-browser         Hide the browser

    -j --json               Output JSON data
    
    -t --table              Output an HTML table

    --html                  Use the page's HTML code as input (filepath specified with --in) instead of 
                            browsing automatically.

    -C --credentials=FILE   Use FILE (.env format) for parcoursup credentials.
                            keys: PARCOURSUP_ID (N° de dossier) and PARCOURSUP_PASS (Mot de passe)
                            If not set, asks for credentials.
"""

from docopt import docopt
from parcoursup_dataviz import scraper, table, visualizer
import json

def run():
    args = docopt(__doc__)
    if args["--in"] and not args['--html']:
        data = json.loads(open(args["--in"]).read())
    else:
        data = scraper.run(**args)
    if args['--json']:
        jsoned = json.dumps(data, indent=2)
        if args["--out"]:
            with open(args["--out"]) as file:
                file.write(jsoned)
        else:
            print(jsoned)
    elif args['--table']:
        table.run(data, **args)
    else:
        visualizer.run(data, args)
