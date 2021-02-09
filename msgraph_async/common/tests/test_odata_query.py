import unittest
from msgraph_async.common.odata_query import *


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

    def test_count_set_bad_value(self):
        i = self.get_instance()
        try:
            i.count = 1
            self.fail()
        except ValueError:
            pass

    def test_count_set(self):
        i = self.get_instance()
        i.count = True

    def test_expand_set_bad_value(self):
        i = self.get_instance()
        try:
            i.expand = 1
            self.fail()
        except ValueError:
            pass

    def test_expand_set(self):
        i = self.get_instance()
        i.expand = "groups"

    def test_filter_set_bad_value(self):
        i = self.get_instance()
        try:
            i.filter = 1
            self.fail()
        except ValueError:
            pass

    def test_select_set_bad_value(self):
        i = self.get_instance()
        try:
            i.select = 1
            self.fail()
        except ValueError:
            pass

    def test_select_set_bad_value2(self):
        i = self.get_instance()
        try:
            i.select = ["valid", 10]
            self.fail()
        except ValueError:
            pass

    def test_select_set(self):
        i = self.get_instance()
        i.select = ["firstName", "lastName"]

    def test_top_set_bad_value(self):
        i = self.get_instance()
        try:
            i.top = "10"
            self.fail()
        except ValueError:
            pass

    def test_top_set(self):
        i = self.get_instance()
        i.top = 10

    def test_top_query(self):
        i = self.get_instance()
        i.top = 10
        self.assertEqual(str(i), "?$top=10")

    def test_top_and_select_query(self):
        i = self.get_instance()
        i.top = 10
        i.select = ["subject", "sender"]
        self.assertEqual(str(i), "?$select=subject,sender&$top=10")

    def test_filter_query(self):
        i = self.get_instance()

        constrain1 = Constrain("city", LogicalOperator.NE, "New-York")
        constrain2 = Constrain("displayName", LogicalOperator.EQ, "Noam Meirovitch")

        f = Filter([constrain1, constrain2], LogicalConnector.OR)

        i.filter = f

        self.assertEqual("?$filter=city ne New-York or displayName eq Noam Meirovitch", str(i))

    def test_count_expand_filter_select_top_query(self):
        i = self.get_instance()

        constrain1 = Constrain("city", LogicalOperator.NE, "New-York")
        constrain2 = Constrain("displayName", LogicalOperator.EQ, "Noam Meirovitch")
        f = Filter([constrain1, constrain2], LogicalConnector.OR)

        i.count = True
        i.expand = "groups"
        i.filter = f
        i.top = 15
        i.select = ["displayName", "firstName", "lastName"]

        self.assertEqual("?$count=true&$expand=groups&$filter=city ne New-York or displayName eq Noam Meirovitch&$select=displayName,firstName,lastName&$top=15", str(i))
