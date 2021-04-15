#!/usr/bin/env python3

__author__ = "Jochen Breuer"
__email__ = "jbreuer@suse.de"
__license__ = "MIT"

import os
import sys
import time
import pickle
import typing
import bugzilla

from bugzilla.bug import Bug
from datetime import datetime
from persistence import QuestDB
from toml_config import get_settings


def get_bugs_for_product(
    product: str, bgz_settings: typing.Dict[str, str], use_cache=False
) -> typing.List[Bug]:
    """
    Fetches bugs for a specific product either from cache or loads them from bugzilla.
    """
    filename = "cache-{}.tmp".format(product)
    if os.path.exists(filename) and use_cache:
        with open(filename, "rb") as f:
            bugs = pickle.load(f)
    else:
        with open(filename, "wb") as f:
            bugs = load_bugs_for_product(product, bgz_settings)
            pickle.dump(bugs, f)
    return bugs


def load_bugs_for_product(
    product: str, bgz_settings: typing.Dict[str, str]
) -> typing.List[Bug]:
    """
    Fetches and returns list of bugs for a specific product.
    """
    bzapi = bugzilla.Bugzilla(bgz_settings["url"])
    bzapi.login(user=bgz_settings["username"], password=bgz_settings["password"])
    query = bzapi.build_query(product=product)
    return bzapi.query(query)


def group_bugs_by_assignee(
    bugs: typing.List[Bug],
) -> typing.Dict[str, typing.List[Bug]]:
    """
    Groups list of bugzilla bugs by assignee: Dict[email, (Bug, …)]
    """
    grouped_bugs: typing.Dict[str, typing.List[Bug]] = {}
    for bug in bugs:
        if bug.assigned_to not in grouped_bugs:
            grouped_bugs[bug.assigned_to] = []
        grouped_bugs[bug.assigned_to].append(bug)
    return grouped_bugs


def group_bugs_by_component(
    bugs: typing.List[Bug],
) -> typing.Dict[str, typing.List[Bug]]:
    """
    Groups list of bugzilla bugs by component: Dict[component, (Bug, …)]
    """
    grouped_bugs: typing.Dict[str, typing.List[Bug]] = {}
    for bug in bugs:
        if bug.component not in grouped_bugs:
            grouped_bugs[bug.component] = []
        grouped_bugs[bug.component].append(bug)
    return grouped_bugs


def group_bugs_by_status(
    bugs: typing.List[Bug],
) -> typing.Dict[str, typing.List[Bug]]:
    """
    Groups list of bugzilla bugs by status: Dict[status, (Bug, …)]
    """
    grouped_bugs: typing.Dict[str, typing.List[Bug]] = {}
    for bug in bugs:
        if bug.status not in grouped_bugs:
            grouped_bugs[bug.status] = []
        grouped_bugs[bug.status].append(bug)
    return grouped_bugs


def is_l3(bug: Bug) -> bool:
    """
    Checks if this bug is or was an l3.
    """
    return "wasL3:" in bug.whiteboard or "openL3:" in bug.whiteboard


def has_needinfo(bug: Bug) -> bool:
    """
    Checks if the needinfor flag is set.
    """
    return any(flag.get("name", "") == "needinfo" for flag in bug.flags)


def main(options):
    settings = get_settings()
    db_settings = settings["questdb"]
    products = settings["bugzilla"]["products"]
    time: datetime = datetime.now()

    db = QuestDB()
    db.connect(db_settings)
    db.setup_tables()

    for product in products:
        print("Product: {}".format(product))
        bugzilla_bugs = get_bugs_for_product(
            product, settings["bugzilla"], use_cache=options.get("--use-cache", False)
        )
        print("Found %d bugs with our query" % len(bugzilla_bugs))
        bugzilla_l3s = [bug for bug in bugzilla_bugs if is_l3(bug)]

        # Bugs by status
        grouped_bugs = group_bugs_by_status(bugzilla_bugs)
        for status, bugs in grouped_bugs.items():
            db.insert_status(product, status, len(bugs), time)

        # Bugs by component
        grouped_bugs = group_bugs_by_component(bugzilla_bugs)
        for component, bugs in grouped_bugs.items():
            db.insert_component(product, component, len(bugs), time)

        # L3 bugs
        l3s = group_bugs_by_status(bugzilla_l3s)
        for status, bugs in l3s.items():
            db.insert_l3(product, status, len(bugs), time)

        # L3 cases
        results = {"open": 0, "closed": 0}
        for l3 in bugzilla_l3s:
            results["open"] += l3.whiteboard.count("openL3:")
            results["closed"] += l3.whiteboard.count("wasL3:")
        db.insert_l3_cases(product, "open", results["open"], time)
        db.insert_l3_cases(product, "closed", results["closed"], time)

        # Bugs per priority
        results = {"p1": 0, "p2": 0, "p3": 0}
        for bug in bugzilla_bugs:
            prio = bug.priority[:2].lower()
            if prio in results:
                results[prio] += 1
        for prio, count in results.items():
            db.insert_priority(product, prio, count, time)

        # Open bugs per assignee
        open_bugs = [bug for bug in bugzilla_bugs if bug.status != "RESOLVED"]
        grouped_bugs = group_bugs_by_assignee(open_bugs)
        for email, bugs in grouped_bugs.items():
            db.insert_assigned(product, email, len(bugs), time)
