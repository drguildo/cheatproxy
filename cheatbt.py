import logging
import urlparse

from odict import OrderedDict

def load_mappings(fname="trackers"):
    """
    Initialises tracker to ratio multiple mappings from the specified
    file.
    """

    logger = logging.getLogger("cheatbt")
    logger.info('loading mappings from "' + fname + '"')

    f = open(fname)
    mappings = {}

    for l in f:
        tracker, multiple = l.split(":")
        mappings[tracker.strip()] = int(multiple.strip())

    f.close()

    if "default" not in mappings:
        mappings["default"] = 1

    return mappings

def cheat(url, mappings):
    """
    Modifies BitTorrent tracker URLs, faking the amount of data
    uploaded. All other URLs should pass through unimpeded.
    """

    parsed = urlparse.urlparse(url)

    if "=" not in parsed.query:
        return url

    query = OrderedDict([i.split("=") for i in parsed.query.split("&")])
    if "uploaded" not in query or query["uploaded"] == "0":
        return url

    if parsed.hostname in mappings:
        multiple = mappings[parsed.hostname]
    else:
        if "default" in mappings:
            multiple = mappings["default"]
        else:
            return url

    # Don't bother munging the URL if the upload amount isn't going
    # to change.
    if multiple == 1:
        return url

    fakeupload = int(query["uploaded"])

    logger = logging.getLogger("cheatbt")
    logger.debug("%s: %d -> %d" % (parsed.hostname, fakeupload,
                                   fakeupload * multiple))

    fakeupload = fakeupload * multiple
    query["uploaded"] = str(fakeupload)

    new_query = ""
    for k in query.keys():
        new_query += k + "=" + query[k] + "&"
    new_query = new_query[:-1] # Remove trailing "&"

    # <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
    new_url = urlparse.urlunparse((parsed.scheme, parsed.netloc, parsed.path,
                                   parsed.params, new_query, parsed.fragment))

    return new_url
