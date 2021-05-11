__author__ = "Jochen Breuer"
__email__ = "jbreuer@suse.de"
__license__ = "MIT"

import os
import pickle
import typing
import bugzilla

from bugzilla.bug import Bug


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
