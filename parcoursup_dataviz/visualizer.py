from typing import *
from parcoursup_dataviz import scraper
from matplotlib.pyplot import *
import json
import re

import collections


def flatten(d, parent_key="", sep="."):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def truncate_title(title: str):
    truncated = ""
    for c in title:
        truncated += c
        if c in (")", "- -"):
            truncated += "\n"
    return truncated


# Aggregate by wish
by_date = scraper.run()
dates = list(by_date.keys())
by_wish: Dict[str, Any] = {}
for date, wishes in by_date.items():
    for wish in wishes:
        if "group_rank" in wish["ranks"].keys():
            print(
                f"ranks.group_rank has been renamed to ranks.calllist_rank\nPlease update your cached JSON in ~/.cache/automation-parcoursup/data.json or run without --cache"
            )
            exit(1)
        key = wish["id"]
        if key not in by_wish.keys():
            by_wish[key] = []
        computed_data = {}
        if wish["is_internat"] and all(
            [
                wish["internat"][key] is not None
                for key in [
                    "condition_group_waitlist_rank",
                    "condition_rank",
                    "rank",
                    "group_waitlist_rank",
                ]
            ]
        ):
            computed_data = {
                "internat_group_diff": wish["internat"]["condition_group_waitlist_rank"]
                - wish["internat"]["group_waitlist_rank"],
                "internat_rank_diff": wish["internat"]["condition_rank"]
                - wish["internat"]["rank"],
            }
        by_wish[key].append(
            {**wish, "date": date, **computed_data,}
        )

wishes_count = len(by_wish.keys())
fig = figure()
fig, axs = subplots(wishes_count)
fig.set_size_inches(10, wishes_count * 6, forward=True)
fig.tight_layout()
idx = 0

# TODO Add missing dates so that all wishes have the same x axis
for wish_id, wish in by_wish.items():
    is_internat = wish[0]["is_internat"]
    name = wish[0]["name"]

    def data(*keys):
        keystring = ".".join(keys)
        return [flatten(d)[keystring] for d in wish]

    if not is_internat:
        axs[idx].plot(data("date"), data("ranks", "rank"), color="black")
        axs[idx].plot(data("date"), data("ranks", "waitlist_length"), color="blue")
        axs[idx].legend(("Position", "Taille de la file d'attente"))
        # plot(data('date'), data('ranks', 'last_year_max_admitted_rank'), color='red', ls='--')
        # plot(data('date'), data('ranks', 'calllist_rank'), color='red')
    else:
        axs[idx].plot(
            data("date"), data("internat", "group_waitlist_rank"), color="blue"
        )
        axs[idx].plot(
            data("date"),
            data("internat", "condition_group_waitlist_rank"),
            color="blue",
            ls="--",
        )
        axs[idx].plot(data("date"), data("internat", "rank"), color="black")
        axs[idx].plot(
            data("date"), data("internat", "condition_rank"), color="black", ls="--"
        )
        axs[idx].legend(
            (
                "Place dans le groupe",
                "Condition pour rentrer",
                "Classement",
                "Condition pour rentrer",
            )
        )
        # plot(data("date"), data("internat", "group_waitlist_rank"), color="blue")
        # plot(data("date"), data("internat", "rank"), color="black")
        # plot(
        #     data("date"),
        #     data("internat", "condition_group_waitlist_rank"),
        #     color="blue",
        #     ls="--",
        # )
        # plot(data("date"), data("internat", "condition_rank"), color="black", ls="--")
    axs[idx].set_title(truncate_title(name))
    idx += 1
subplots_adjust(hspace=0.4)
# suptitle('Parcoursup - Vœux en liste d\'attente')
fig.savefig("voeux-en-attente-parcoursup.png", dpi=100)
