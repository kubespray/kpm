import logging
from tabulate import tabulate
from kpm.utils import colorize

logger = logging.getLogger(__name__)


def print_packages(packages):
    header = ['app', 'release', 'downloads', 'manifests']
    table = []
    for p in packages:
        release = p["default"]
        manifests = ", ".join(p['manifests'])
        table.append([p['name'], release, str(p.get('downloads', '-')), manifests])
    print tabulate(table, header)


def print_deploy_result(table):
    header = ["package", "release", "type", "name",  "namespace", "status"]
    print "\n"
    for r in table:
        status = r.pop()
        r.append(colorize(status))

    print tabulate(table, header)


def print_channels(channels):
    header = ['channel', 'release']
    table = []
    for channel in channels:
        table.append([channel['name'], channel['current']])
    return tabulate(table, header)
