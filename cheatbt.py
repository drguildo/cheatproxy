import string
from urlparse import urlparse

from odict import OrderedDict

class CheatBT(object):
    # TODO: Reload when file changes.
    def __init__(self, filename="trackers"):
        """Initialises tracker to ratio multiple mappings from the specified
        file.

        >>> c = CheatBT("test/test1")
        >>> c.map["default"]
        2
        >>> c.map["tracker1.example.net"]
        0
        >>> c.map["tracker2.example.net"]
        10
        >>> c.map["tracker3.example.net"]
        123
        >>> c.map["tracker4.example.net"]
        456
        >>> c.map["tracker5.example.net"]
        789
        >>> c = CheatBT("test/nodefault")
        >>> c.map["default"]
        1
        """
        file = open(filename)
        self.map = {}
        for line in file:
            k, v = line.split(":")
            self.map[k.strip()] = int(v.strip())
        if "default" not in self.map:
            self.map["default"] = 1

    def cheat_url(self, url, verbose=False):
        """Modifies BitTorrent tracker URLs, faking the amount of data
        uploaded. All other URLs should pass through unimpeded.

        >>> c = CheatBT("test/test1")
        >>> c.cheat_url("http://www.example.net/")
        'http://www.example.net/'
        >>> c.cheat_url("http://www.example.net/?test")
        'http://www.example.net/?test'
        >>> c.cheat_url("http://www.example.net/test?test")
        'http://www.example.net/test?test'
        >>> c.cheat_url("http://www.example.net/test?test=val")
        'http://www.example.net/test?test=val'
        >>> c.cheat_url("http://www.example.net/test?uploaded=0")
        'http://www.example.net/test?uploaded=0'
        >>> c.cheat_url("http://www.example.net/test?uploaded=123456")
        'http://www.example.net/test?uploaded=246912'
        >>> c.cheat_url("http://www.example.net/test?test1=val&test2=val&downloaded=5&uploaded=10")
        'http://www.example.net/test?test1=val&test2=val&downloaded=5&uploaded=20'
        >>> c.cheat_url("http://www.example.net:6969/")
        'http://www.example.net:6969/'
        >>> c.cheat_url("http://www.example.net:6969/?test")
        'http://www.example.net:6969/?test'
        >>> c.cheat_url("http://www.example.net:6969/test?test")
        'http://www.example.net:6969/test?test'
        >>> c.cheat_url("http://www.example.net:6969/test?test=val")
        'http://www.example.net:6969/test?test=val'
        >>> c.cheat_url("http://www.example.net:6969/test?uploaded=0")
        'http://www.example.net:6969/test?uploaded=0'
        >>> c.cheat_url("http://www.example.net:6969/test?uploaded=123456")
        'http://www.example.net:6969/test?uploaded=246912'
        >>> c.cheat_url("http://www.example.net:6969/test?test1=val&test2=val&downloaded=5&uploaded=10")
        'http://www.example.net:6969/test?test1=val&test2=val&downloaded=5&uploaded=20'
        """

        parsed = urlparse(url)

        if parsed.query != "" and "=" in parsed.query:
            query = OrderedDict([i.split("=") for i in parsed.query.split("&")])
            # TODO: Don't bother munging URL if multiple is set to 1.
            #if "uploaded" in query and query["uploaded"] != "0":
            if "uploaded" in query:
                if verbose:
                    print parsed.hostname + ": " + query["uploaded"],
                if parsed.hostname in self.map:
                    multiple = self.map[parsed.hostname]
                else:
                    multiple = self.map["default"]
                # TODO: Skew fake value so it's not an exact multiple of the
                # real value.
                query["uploaded"] = str(int(query["uploaded"]) * multiple)
                if verbose:
                    print "-> " + query["uploaded"] + " (%d)" % multiple

                new_query = ""
                for k in query.keys():
                    new_query += k + "=" + query[k] + "&"
                new_query = new_query[:-1]

                # <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
                new_url = ""
                if parsed.scheme:
                    new_url += parsed.scheme + "://"
                if parsed.netloc:
                    new_url += parsed.netloc
                if parsed.path:
                    new_url += parsed.path
                if parsed.params:
                    new_url += ";" + parsed.params
                new_url += "?" + new_query
                if parsed.fragment:
                    new_url += "#" + parsed.fragment

                url = new_url

        return url

if __name__ == "__main__":
    import doctest
    doctest.testmod()
