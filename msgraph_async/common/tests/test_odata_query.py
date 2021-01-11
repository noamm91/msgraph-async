import unittest
from msgraph_async.common.odata_query import ODataQuery


class TestODataQuery(unittest.TestCase):

    def setUp(self):
        pass

    @classmethod
    def setUpClass(cls):
        pass

    def get_instance(self):
        return ODataQuery()

    def test_empty_odata(self):
        i = self.get_instance()
        self.assertEqual("EMPTY OPEN DATA QUERY", str(i))

    def test_top_query(self):
        i = self.get_instance()
        i.top = 10
        self.assertEqual(str(i), "?$top=10")

    def test_top_and_select_query(self):
        i = self.get_instance()
        i.top = 10
        i.select = ["subject", "sender"]
        self.assertEqual(str(i), "?$select=subject,sender&$top=10")
