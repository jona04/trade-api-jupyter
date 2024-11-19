import constants.defs as defs
from infrastructure.quotehistory_collection import quotehistoryCollection as qc


def make_option(k):
    return dict(key=k, label=k, value=k)


def get_options():
    qc.LoadQuotehistoryDBFiltered()
    
    ps = [p for p in qc.quotehistory_dict.keys()]
    ps.sort()

    return dict(
        granularities=[make_option(g) for g in defs.TFS.keys()],
        pairs=[make_option(p) for p in ps]
    )