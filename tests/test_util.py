import unittest
from connexion_plus import Util


class Test_Util(unittest.TestCase):
    def setUp(self):
        import requests
        import yaml
        self.oai = yaml.full_load(requests.get(
            "https://raw.githubusercontent.com/OAI/OpenAPI-Specification/master/examples/v2.0/yaml/petstore.yaml").text)
        self.oai_file = yaml.full_load(open("tests/petstore.yaml", "r").read())
        self.oai_list = [self.oai, self.oai_file]

    def test_is_url(self):
        self.assertTrue(Util.is_url("http://google.de"))
        self.assertTrue(Util.is_url("https://google.de"))
        self.assertTrue(Util.is_url("http://google.de/"))
        self.assertTrue(Util.is_url("https://google.de/"))
        self.assertTrue(Util.is_url(
            "https://www.google.de/search?q=connexion"))
        self.assertTrue(Util.is_url("https://www.google"))

        self.assertFalse(Util.is_url("https:/www.google.de"))
        self.assertFalse(Util.is_url("www.google.de"))

        self.assertFalse(Util.is_url("./tests/test_util.py"))

    def test_is_file(self):

        self.assertTrue(Util.is_file("./tests/test_util.py"))

        self.assertFalse(Util.is_file("./"))
        self.assertFalse(Util.is_file("/home"))
        self.assertFalse(Util.is_file("/"))
        self.assertFalse(Util.is_file("."))
        self.assertFalse(Util.is_file("~/"))
        self.assertFalse(Util.is_file("http://google.de"))
        self.assertFalse(Util.is_file(
            "https://www.google.de/search?q=connexion"))

    def test_internal_oai(self):
        self.assertEqual(Util.internal_load_oai(
            "https://raw.githubusercontent.com/OAI/OpenAPI-Specification/master/examples/v2.0/yaml/petstore.yaml"), self.oai)
        self.assertEqual(Util.internal_load_oai("tests/petstore.yaml"), self.oai)
        self.assertEqual(Util.internal_load_oai("./tests/petstore.yaml"), self.oai)

        with self.assertRaises(ValueError):
            Util.internal_load_oai("https:/www.google.de")

    def test_load_oai(self):
        self.assertEqual(Util.load_oai(
            "https://raw.githubusercontent.com/OAI/OpenAPI-Specification/master/examples/v2.0/yaml/petstore.yaml"), [self.oai])

        oai_list = [
            "https://raw.githubusercontent.com/OAI/OpenAPI-Specification/master/examples/v2.0/yaml/petstore.yaml", "tests/petstore.yaml"]
        self.assertEqual(Util.load_oai(oai_list), self.oai_list)
