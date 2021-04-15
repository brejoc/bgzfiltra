import os
import sys
import toml


def get_settings():
    """\
    Loads TOML settings from one of the defined paths:
        ./.bgzfiltra.toml
        ./bgzfiltra.toml
        ~/.bgzfiltra.toml
        ~/.config/bgzfiltra.toml
        /etc/bgzfiltra.toml
    """
    paths = (
        "./.bgzfiltra.toml",
        "./bgzfiltra.toml",
        "~/.bgzfiltra.toml",
        "~/.config/bgzfiltra.toml",
        "/etc/bgzfiltra.toml",
    )
    settings = None
    for path in paths:
        path = os.path.expanduser(path)
        if (
            os.path.isfile(path)
            and not os.path.isdir(path)
            and not os.path.islink(path)
        ):
            settings = toml.load(path)
            break
    if not settings:
        print(
            "Could not find settings file in any of these locations:\n{}".format(
                "\n".join(paths)
            )
        )
        sys.exit(3)
    _bugzilla_section_checks(settings)
    _questdb_section_checks(settings)
    return settings


def _questdb_section_checks(settings):
    """
    QuestDB specific setting validations.
    """
    if not settings.get("questdb"):
        print(
            'questdb section missing in settings file:\n[questdb]\nuser = "admin"\n…',
            file=sys.stderr,
        )
        sys.exit(2)
    if "user" not in settings["questdb"]:
        print(
            'username definition missing in questdb section: user = "admin"',
            file=sys.stderr,
        )
        sys.exit(2)
    if "password" not in settings["questdb"]:
        print(
            'password definition missing in questdb section: password = "mypassword"',
            file=sys.stderr,
        )
        sys.exit(2)
    if "host" not in settings["questdb"]:
        print(
            'host definition missing in questdb section: host = "127.0.0.1"',
            file=sys.stderr,
        )
        sys.exit(2)
    if "port" not in settings["questdb"]:
        print(
            'port definition missing in questdb section: port = "8812"',
            file=sys.stderr,
        )
        sys.exit(2)
    if "database" not in settings["questdb"]:
        print(
            'database definition missing in questdb section: database = "mydb"',
            file=sys.stderr,
        )
        sys.exit(2)


def _bugzilla_section_checks(settings):
    """
    Bugzilla specific setting validations.
    """
    if not settings.get("bugzilla"):
        print(
            'bugzilla section missing in settings file:\n[bugzilla]\nusernames = "foo@bar.de"\npassword = "mypassword"',
            file=sys.stderr,
        )
        sys.exit(2)
    if "url" not in settings["bugzilla"]:
        print(
            'url definition missing in settings file: url = "bugzilla.myurl.com"',
            file=sys.stderr,
        )
        sys.exit(2)
    if "username" not in settings["bugzilla"]:
        print(
            'username definition missing in settings file: usernames = "foo@bar.de"',
            file=sys.stderr,
        )
        sys.exit(2)
    if "password" not in settings["bugzilla"]:
        print(
            'password definition missing in settings file: password = "mypassword"',
            file=sys.stderr,
        )
        sys.exit(2)
