from semantic_version import Version, Spec


def versions(versions_str, stable=False):
    if stable:
        return [Version(x) for x in versions_str if len(x.split("-")) == 1]
    else:
        return [Version(x) for x in versions_str]


def last_version(versions_str, stable=False):
    return sorted(versions(versions_str, stable))[-1]


def select_version(versions_str, query, stable=False):
    if isinstance(query, str):
        query = query.split(",")
    query = [x.replace(" ", "") for x in query]
    stable = True
    if "-" in str(query):
        stable = False
    spec = Spec(*query)
    return spec.select(versions(versions_str, stable))
