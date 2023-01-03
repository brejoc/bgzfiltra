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


def __get_bugzilla_api(bgz_settings: typing.Dict[str, str]) -> bugzilla.Bugzilla:
    print("Trying to authenticate to Bugzilla")
    bzapi = bugzilla.Bugzilla(bgz_settings["url"], api_key=bgz_settings["apikey"], sslverify=bgz_settings["sslverify"])
    try:
        if not bzapi.logged_in:
            raise Exception("Authentication token is invalid or user is already logged out")
    except Exception as exc:
        if bgz_settings["use_legacy_credentials"]:
            print(f"There was an error authenticating Bugzilla using API KEY: {exc}")
            print("Trying authentication using legacy username and password")
            bzapi = bugzilla.Bugzilla(bgz_settings["url"], sslverify=bgz_settings["sslverify"])
            bzapi.login(user=bgz_settings["username"], password=bgz_settings["password"])
        else:
            raise exc
    print("Bugzilla authentication was successful!")
    return bzapi


def load_bugs_for_product(
    product: str, bgz_settings: typing.Dict[str, str]
) -> typing.List[Bug]:
    """
    Fetches and returns list of bugs for a specific product.
    """
    bzapi = __get_bugzilla_api(bgz_settings)
    query = bzapi.build_query(product=product)
    return bzapi.query(query)
