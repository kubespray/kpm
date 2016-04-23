import logging
from tabulate import tabulate
from kpm.utils import colorize

logger = logging.getLogger(__name__)


def print_packages(packages):
    header = ['app', 'version', 'downloads']
    table = []

    for p in packages:
        table.append([p['name'], p['version'],  str(p.get('downloads', '-'))])
    print tabulate(table, header)


def print_deploy_result(table):
    header = ["package", "version", "type", "name",  "namespace", "status"]
    print "\n"
    for r in table:
        status = r.pop()
        r.append(colorize(status))

    print tabulate(table, header)
