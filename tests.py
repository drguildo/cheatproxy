import unittest

import cheatbt

class TestLoadMappings(unittest.TestCase):

    def setUp(self):
        self.parsing = cheatbt.load_mappings("test/parsing")
        self.nodefault = cheatbt.load_mappings("test/nodefault")

    def test_parsing(self):
        self.assertEqual(self.parsing["tracker1.example.net"], 0)
        self.assertEqual(self.parsing["tracker2.example.net"], 10)
        self.assertEqual(self.parsing["tracker3.example.net"], 123)
        self.assertEqual(self.parsing["tracker4.example.net"], 456)
        self.assertEqual(self.parsing["tracker5.example.net"], 789)

    def test_nodefault(self):
        self.assertEqual(self.nodefault["default"], 1)

class TestCheat(unittest.TestCase):

    def setUp(self):
        self.mappings = {"default": 2}

    def test_normal(self):
        """
        These URLs should pass through without modification.
        """

        urls = (
            "http://www.example.net/",
            "http://www.example.net/?test",
            "http://www.example.net/test?test",
            "http://www.example.net/test?test=val",
            "http://www.example.net/test?uploaded=0",
            "http://www.example.net:6969/",
            "http://www.example.net:6969/?test",
            "http://www.example.net:6969/test?test",
            "http://www.example.net:6969/test?test=val",
            "http://www.example.net:6969/test?uploaded=0"
            )

        for url in urls:
            self.assertEqual(cheatbt.cheat(url, self.mappings), url)

    def test_modify_upload(self):
        """
        Upload parameter should be modified.
        """

        urls = (
            ("http://www.example.net/test?uploaded=123456",
             "http://www.example.net/test?uploaded=246912"),
            ("http://www.example.net/test?test1=val&test2=val&downloaded=5&uploaded=10",
             "http://www.example.net/test?test1=val&test2=val&downloaded=5&uploaded=20"),
            ("http://www.example.net:6969/test?uploaded=123456",
             "http://www.example.net:6969/test?uploaded=246912"),
            ("http://www.example.net:6969/test?test1=val&test2=val&downloaded=5&uploaded=10",
             "http://www.example.net:6969/test?test1=val&test2=val&downloaded=5&uploaded=20")
            )

        for pair in urls:
            self.assertEqual(cheatbt.cheat(pair[0], self.mappings), pair[1])

if __name__ == '__main__':
    unittest.main()
