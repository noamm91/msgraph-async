import os
import json
import asynctest
import asyncio
from datetime import datetime, timedelta
from msgraph_async.client.client import GraphAdminClient
from msgraph_async.common.constants import *
from msgraph_async.common.exceptions import *
from msgraph_async.common.odata_query import *
import requests


class TestClient(asynctest.TestCase):
    _test_app_id = None
    _test_app_secret = None
    _test_tenant_id = None
    _token = None
    _user_id = None
    _total_users_count = None
    _bulk_size = None
    _notification_url = None
    _valid_message_id = None

    def setUp(self):
        pass

    @classmethod
    def setUpClass(cls):
        credentials_file = os.path.join(os.path.dirname(__file__), "test_credentials")
        with open(credentials_file) as fp:
            details = json.load(fp)

        cls._test_app_id = details["app_id"]
        cls._test_app_secret = details["app_secret"]
        cls._test_tenant_id = details["tenant_id"]
        cls._user_id = details["user_id"]
        cls._notification_url = details["notification_url"]
        cls._valid_message_id = details["valid_message_id"]
        cls._total_users_count = 25
        cls._bulk_size = 10

        token_params = {
            'grant_type': 'client_credentials',
            "scope": "https://graph.microsoft.com/.default",
            'client_id': cls._test_app_id,
            'client_secret': cls._test_app_secret,
        }

        r = requests.post(f"https://login.microsoftonline.com/{cls._test_tenant_id}/oauth2/v2.0/token",
                          data=token_params)
        res_json = r.json()
        cls._token = res_json['access_token']

    def get_instance(self):
        return GraphAdminClient(enable_logging=True)

    async def test_list_users_bulk_manual_token_with_top(self):
        i = self.get_instance()
        odata_query = ODataQuery()
        odata_query.top = TestClient._bulk_size

        res, status = await i.list_users_bulk(token=TestClient._token, odata_query=odata_query)

        expected = min(TestClient._bulk_size, TestClient._total_users_count)
        self.assertEqual(expected, len(res["value"]))

    async def test_list_users_bulk_manual_token_with_top_and_starts_with_filter(self):
        i = self.get_instance()
        odata_query = ODataQuery()
        odata_query.top = TestClient._bulk_size
        odata_query.filter = Filter([Constrain("displayName", LogicalOperator.STARTS_WITH, "N")])
        res, status = await i.list_users_bulk(token=TestClient._token, odata_query=odata_query)
        self.assertEqual(status, HTTPStatus.OK)

    async def test_list_users_bulk_managed_token_with_top(self):
        i = self.get_instance()
        await i.manage_token(TestClient._test_app_id, TestClient._test_app_secret, TestClient._test_tenant_id)
        odata_query = ODataQuery()
        odata_query.top = TestClient._bulk_size

        res, status = await i.list_users_bulk(odata_query=odata_query)

        expected = min(TestClient._bulk_size, TestClient._total_users_count)
        self.assertEqual(expected, len(res["value"]))

    async def test_manage_token(self):
        i = self.get_instance()
        await i.manage_token(TestClient._test_app_id, TestClient._test_app_secret, TestClient._test_tenant_id)
        self.assertEqual(True, i.is_managed)
        token = i.token
        self.assertIsNotNone(token)

    async def test_manage_token_refreshing(self):
        i = self.get_instance()
        i._token_refresh_interval_sec = 5
        await i.manage_token(TestClient._test_app_id, TestClient._test_app_secret, TestClient._test_tenant_id)
        self.assertEqual(True, i.is_managed)
        token1 = i.token
        self.assertIsNotNone(token1)
        await asyncio.sleep(7)
        token2 = i.token
        self.assertIsNotNone(token2)
        self.assertNotEqual(token1, token2)

    async def test_get_user(self):
        i = self.get_instance()
        res, status = await i.get_user(TestClient._user_id, token=TestClient._token)
        self.assertEqual(status, HTTPStatus.OK)

    async def test_acquire_token(self):
        i = self.get_instance()
        token, status = await i.acquire_token(TestClient._test_app_id, TestClient._test_app_secret, TestClient._test_tenant_id)
        self.assertEqual(status, HTTPStatus.OK)
        self.assertIsNotNone(token["access_token"])

    async def test_list_all_users(self):
        i = self.get_instance()
        users = []
        async for user in i.list_all_users(token=TestClient._token):
            users.append(user)
        self.assertEqual(TestClient._total_users_count, len(users))

    async def test_mailbox_subscription_lifecycle(self):
        i = self.get_instance()
        minutes_to_expire = 10
        # time_to_expire = str(datetime.utcnow() + timedelta(minutes=minutes_to_expire))
        res, status = await i.create_subscription(
            "created", TestClient._notification_url, SubscriptionResources.Mailbox, minutes_to_expire,
            user_id=TestClient._user_id, token=TestClient._token)

        subscription_id = res.get("id")
        self.assertIsNotNone(subscription_id)

        self.assertEqual(status, HTTPStatus.CREATED)

        await asyncio.sleep(2)

        minutes_to_expire = 15
        res, status = await i.renew_subscription(subscription_id, minutes_to_expire, token=TestClient._token)

        self.assertEqual(status, HTTPStatus.OK)

        await asyncio.sleep(2)

        res, status = await i.delete_subscription(subscription_id, token=TestClient._token)

        self.assertEqual(status, HTTPStatus.NO_CONTENT)

    async def test_create_subscription_resource_no_user_id(self):
        i = self.get_instance()
        minutes_to_expire = 10
        try:
            await i.create_subscription(
                "created", TestClient._notification_url, SubscriptionResources.Mailbox, minutes_to_expire,
                token=TestClient._token)
            self.fail("should raise an exception")
        except GraphClientException:
            pass

    async def test_list_user_mails_bulk_manual_token(self):
        i = self.get_instance()

        res, status = await i.list_user_mails_bulk(TestClient._user_id, token=TestClient._token)

        self.assertEqual(status, HTTPStatus.OK)

    async def test_list_more_user_mails_manual_token(self):
        i = self.get_instance()

        q = ODataQuery()
        q.top = 6
        start = "2021-01-01T00:00:00.000Z"
        end = "2021-01-02T00:00:00.000Z"
        constrains = [Constrain("receivedDateTime", LogicalOperator.GT, start),
                      Constrain("receivedDateTime", LogicalOperator.LT, end)]
        q.filter = Filter(constrains, LogicalConnector.AND)

        res, status = await i.list_user_mails_bulk(TestClient._user_id, token=TestClient._token, odata_query=q)

        self.assertEqual(status, HTTPStatus.OK)
        next = res.get("@odata.nextLink")
        if not next:
            self.fail("should have next..")

        res, status = await i.list_more_user_mails(next, token=TestClient._token)

        self.assertEqual(status, HTTPStatus.OK)

    async def test_list_all_user_mails(self):
        i = self.get_instance()

        q = ODataQuery()
        q.top = 6
        start = "2021-01-01T00:00:00.000Z"
        end = "2021-01-02T00:00:00.000Z"
        constrains = [Constrain("receivedDateTime", LogicalOperator.GT, start),
                      Constrain("receivedDateTime", LogicalOperator.LT, end)]
        q.filter = Filter(constrains, LogicalConnector.AND)

        mails = []
        async for mail in i.list_all_user_mails(TestClient._user_id, token=TestClient._token, odata_query=q):
            mails.append(mail)

        self.assertEqual(9, len(mails))

    async def test_get_mail(self):
        i = self.get_instance()

        mail, status = await i.get_mail(TestClient._user_id, TestClient._valid_message_id, token=TestClient._token)

        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(dict, type(mail))
        self.assertEqual(TestClient._valid_message_id, mail["id"])

    async def test_get_mail_as_mime(self):
        i = self.get_instance()

        mail, status = await i.get_mail(
            TestClient._user_id, TestClient._valid_message_id, as_mime=True, token=TestClient._token)

        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(bytes, type(mail))
