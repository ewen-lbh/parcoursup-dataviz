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


def fill_list_to_len(o: list, target_len: int, fill_with: Any = None) -> list:
    if len(o) >= target_len:
        return o

    to_fill = (target_len - len(o)) * [fill_with]
    return o + to_fill


def run(wishes_data, args):
    # Aggregate by wish
    dates = list(wishes_data.keys())
    by_wish: Dict[str, Any] = {}
    for date, wishes in wishes_data.items():
        for wish in wishes:
            if "group_rank" in wish["ranks"].keys():
                print(
                    f"""ranks.group_rank has been renamed to ranks.calllist_rank.
Please update your JSON file"""
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
                    "internat_group_diff": wish["internat"][
                        "condition_group_waitlist_rank"
                    ]
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

    for wish_id, wish in by_wish.items():
        is_internat = wish[0]["is_internat"]
        name = wish[0]["name"]

        def data(*keys, fill_with: Any = None):
            keystring = ".".join(keys)
            return fill_list_to_len(
                [flatten(d)[keystring] for d in wish],
                target_len=len(dates),
                fill_with=fill_with,
            )

        if not is_internat:
            axs[idx].plot(dates, data("ranks", "rank", fill_with=0), color="black")
            axs[idx].plot(dates, data("ranks", "waitlist_length"), color="blue")
            axs[idx].legend(("Position", "Taille de la file d'attente"))
            # plot(data('date'), data('ranks', 'last_year_max_admitted_rank'), color='red', ls='--')
            # plot(data('date'), data('ranks', 'calllist_rank'), color='red')
        else:
            axs[idx].plot(
                dates,
                data("internat", "group_waitlist_rank", fill_with=0),
                color="blue",
            )
            axs[idx].plot(
                dates,
                data("internat", "condition_group_waitlist_rank"),
                color="blue",
                ls="--",
            )
            axs[idx].plot(dates, data("internat", "rank"), color="black")
            axs[idx].plot(
                dates, data("internat", "condition_rank"), color="black", ls="--"
            )
            axs[idx].legend(
                (
                    "Place dans le groupe",
                    "Condition pour rentrer",
                    "Classement",
                    "Condition pour rentrer",
                )
            )
            # plot(dates, data("internat", "group_waitlist_rank"), color="blue")
            # plot(dates, data("internat", "rank"), color="black")
            # plot(
            #     dates,
            #     data("internat", "condition_group_waitlist_rank"),
            #     color="blue",
            #     ls="--",
            # )
            # plot(dates, data("internat", "condition_rank"), color="black", ls="--")
        axs[idx].set_title(truncate_title(name))
        idx += 1
    subplots_adjust(hspace=0.4)
    # suptitle('Parcoursup - Vœux en liste d\'attente')
    outfile = args["--out"] or "vœux-en-attente-parcoursup.png"
    fig.savefig(outfile, dpi=100)
    print(f"Saved graphs as {outfile}")
