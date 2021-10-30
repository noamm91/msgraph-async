import os
import json
import asynctest
import asyncio
import requests
import urllib
import urllib.parse
from aioresponses import aioresponses
from msgraph_async.client.client import GraphAdminClient
from msgraph_async.common.constants import *
from msgraph_async.common.exceptions import *
from msgraph_async.common.odata_query import *


class TestClient(asynctest.TestCase):
    _test_app_id = None
    _test_app_secret = None
    _one_drive_app_id = None
    _one_drive_app_secret = None
    _test_tenant_id = None
    resource_data_in_subscription_app_id = None
    resource_data_in_subscription_app_secret = None
    _token = None
    _user_id = None
    _site_id = None
    _group_id = None
    _team_id = None
    _channel_id = None
    _total_users_count = None
    _bulk_size = None
    _notification_url = None
    _valid_message_id = None
    _token_subscription_with_resource_data = None
    _one_drive_token = None
    _mail_start_time = None
    _mail_end_time = None
    _expected_count = None
    _mail_to_users = None
    _mail_from_user = None
    _one_drive_file_id = None
    _remote_drive_id = None
    _remote_drive_item_id = None

    def setUp(self):
        pass

    @classmethod
    def setUpClass(cls):
        credentials_file = os.path.join(os.path.dirname(__file__), "test_credentials")
        with open(credentials_file) as fp:
            details = json.load(fp)

        cls._test_app_id = details["app_id"]
        cls._test_app_secret = details["app_secret"]
        cls._one_drive_app_id = details["drive_permissions_app_id"]
        cls._one_drive_app_secret = details["drive_permissions_app_secret"]
        cls._test_tenant_id = details["tenant_id"]
        cls._user_id = details["user_id"]
        cls._site_id = details["site_id"]
        cls._group_id = details["group_id"]
        cls._team_id = details["team_id"]
        cls._channel_id = details["channel_id"]
        cls._one_drive_file_id = details["one_drive_file_id"]
        cls._notification_url = details["notification_url"]
        cls._valid_message_id = details["valid_message_id"]
        cls._resource_data_in_subscription_app_id = details["resource_data_in_subscription_app_id"]
        cls._resource_data_in_subscription_app_secret = details["resource_data_in_subscription_app_secret"]
        cls._mail_start_time = details["mail_start_time"]
        cls._mail_end_time = details["mail_end_time"]
        cls._expected_count = details["expected_mails_count"]
        cls._mail_to_users = details["mail_to_users"]
        cls._mail_from_user = details["mail_from_user"]
        cls._total_users_count = 25
        cls._bulk_size = 10
        cls._remote_drive_id = details["remote_drive_id"]
        cls._remote_drive_item_id = details["remote_drive_item_id"]

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

        token_params = {
            'grant_type': 'client_credentials',
            "scope": "https://graph.microsoft.com/.default",
            'client_id': cls._resource_data_in_subscription_app_id,
            'client_secret': cls._resource_data_in_subscription_app_secret,
        }

        r = requests.post(f"https://login.microsoftonline.com/{cls._test_tenant_id}/oauth2/v2.0/token",
                          data=token_params)
        res_json = r.json()
        cls._token_subscription_with_resource_data = res_json['access_token']

        token_params = {
            'grant_type': 'client_credentials',
            "scope": "https://graph.microsoft.com/.default",
            'client_id': cls._one_drive_app_id,
            'client_secret': cls._one_drive_app_secret,
        }

        r = requests.post(f"https://login.microsoftonline.com/{cls._test_tenant_id}/oauth2/v2.0/token",
                          data=token_params)
        res_json = r.json()
        cls._one_drive_token = res_json['access_token']

    @staticmethod
    def get_instance(mocked_graph_url=None):
        return GraphAdminClient(enable_logging=True, mocked_graph_url=mocked_graph_url)

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
        res, status = await i.renew_subscription(subscription_id, SubscriptionResources.Mailbox, minutes_to_expire,
                                                 token=TestClient._token)

        self.assertEqual(status, HTTPStatus.OK)

        await asyncio.sleep(2)

        res, status = await i.delete_subscription(subscription_id, SubscriptionResources.Mailbox,
                                                  token=TestClient._token)

        self.assertEqual(status, HTTPStatus.NO_CONTENT)

    async def test_tenant_channels_subscription_lifecycle(self):
        i = self.get_instance()

        with open("fake_cert.pem") as f:
            certificate = f.read()

        life_cycle_checks = "https://mila.bitdam.com/api/v1.0/office365/teams/life_cycle_check"

        minutes_to_expire = 3
        res, status = await i.create_subscription(
            "created,updated,deleted", TestClient._notification_url, SubscriptionResources.TenantTeamsChannels,
            minutes_to_expire, life_cycle_url=life_cycle_checks, plain_certificate=certificate,
            token=TestClient._token_subscription_with_resource_data)

        subscription_id = res.get("id")
        self.assertIsNotNone(subscription_id)

        self.assertEqual(status, HTTPStatus.CREATED)

        await asyncio.sleep(2)

        minutes_to_expire = 3
        res, status = await i.renew_subscription(
            subscription_id, SubscriptionResources.TenantTeamsChannels, minutes_to_expire,
            token=TestClient._token_subscription_with_resource_data)

        self.assertEqual(status, HTTPStatus.OK)

        await asyncio.sleep(2)

        res, status = await i.delete_subscription(
            subscription_id, SubscriptionResources.TenantTeamsChannels,
            token=TestClient._token_subscription_with_resource_data)

        self.assertEqual(status, HTTPStatus.NO_CONTENT)

    async def test_create_subscription_resource_no_user_id(self):
        i = self.get_instance()
        minutes_to_expire = 10
        try:
            await i.create_subscription(
                "created", TestClient._notification_url, SubscriptionResources.Mailbox, minutes_to_expire,
                token=TestClient._token)
            self.fail("should raise an exception")
        except GraphClientException as e:
            pass

    async def test_list_user_mails_bulk_manual_token(self):
        i = self.get_instance()

        res, status = await i.list_user_mails_bulk(TestClient._user_id, token=TestClient._token)

        self.assertEqual(status, HTTPStatus.OK)

    async def test_list_more_user_mails_manual_token(self):
        i = self.get_instance()

        q = ODataQuery()
        q.top = 1
        start = TestClient._mail_start_time
        end = TestClient._mail_end_time
        constrains = [Constrain("receivedDateTime", LogicalOperator.GT, start),
                      Constrain("receivedDateTime", LogicalOperator.LT, end)]
        q.filter = Filter(constrains, LogicalConnector.AND)

        res, status = await i.list_user_mails_bulk(TestClient._user_id, token=TestClient._token, odata_query=q)

        self.assertEqual(status, HTTPStatus.OK)
        next = res.get("@odata.nextLink")
        if not next:
            self.fail("should have next..")

        res, status = await i.list_more(next, token=TestClient._token)

        self.assertEqual(status, HTTPStatus.OK)

    async def test_list_all_user_mails(self):
        i = self.get_instance()

        q = ODataQuery()
        q.top = 6
        start = TestClient._mail_start_time
        end = TestClient._mail_end_time
        expected_count = TestClient._expected_count
        constrains = [Constrain("receivedDateTime", LogicalOperator.GT, start),
                      Constrain("receivedDateTime", LogicalOperator.LT, end)]
        q.filter = Filter(constrains, LogicalConnector.AND)

        mails = []
        async for mail in i.list_all_user_mails(TestClient._user_id, token=TestClient._token, odata_query=q):
            mails.append(mail)

        self.assertEqual(expected_count, len(mails))

    async def test_list_all_user_mails_filter_mail_address_ne(self):
        i = self.get_instance()

        q = ODataQuery()
        q.top = 20
        start = "2021-03-01T00:00:00.000Z"
        q.select = ["id", "from", "replyTo", "sentDateTime", "hasAttachments", "receivedDateTime", "subject", "isRead",
                    "parentFolderId", "sender", "toRecipients", "ccRecipients", "bccRecipients", "internetMessageHeaders"]

        constrains = [Constrain("receivedDateTime", LogicalOperator.GT, start),
                      Constrain("sender/emailAddress/address", LogicalOperator.NE, "'test.user@bitdam.com'"),
                      Constrain("isDraft", LogicalOperator.EQ, "false")]
        q.filter = Filter(constrains, LogicalConnector.AND)

        mails = []
        async for mail in i.list_all_user_mails(TestClient._user_id, token=TestClient._token, odata_query=q):
            mails.append(mail)

    async def test_get_mail(self):
        i = self.get_instance()

        mail, status = await i.get_mail(TestClient._user_id, TestClient._valid_message_id, token=TestClient._token)

        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(dict, type(mail))
        self.assertEqual(TestClient._valid_message_id, mail["id"])

    @aioresponses()
    async def test_get_mail_simulating_429(self, mocked_res):
        i = self.get_instance()

        url = "https://graph.microsoft.com/v1.0/users/uid/messages/mid"
        error_dict = {"error": "maximum bla bla bla"}
        mocked_res.get(url, status=429, body=json.dumps(error_dict).encode())
        try:
            await i.get_mail("uid", "mid", token=TestClient._token)
            self.fail("should raise an exception")
        except BaseHttpError as e:
            self.assertEqual(e.status, HTTPStatus.TOO_MANY_REQUESTS)
            self.assertEqual(e.request_url, url)
            self.assertEqual(e.response_content, error_dict)
            self.assertIsNotNone(e.response_headers)

    @aioresponses()
    async def test_get_mail_broad_exception_clause(self, mocked_res):
        i = self.get_instance()

        url = "https://graph.microsoft.com/v1.0/users/uid/messages/mid"
        error_dict = {"error": "maximum bla bla bla"}
        mocked_res.get(url, status=429, body=json.dumps(error_dict).encode())
        try:
            await i.get_mail("uid", "mid", token=TestClient._token)
            self.fail("should raise an exception")
        except (TooManyRequests, InternalServerError, ServiceUnavailable) as e:
            self.assertEqual(e.request_url, url)
            self.assertEqual(e.status, HTTPStatus.TOO_MANY_REQUESTS)
            self.assertEqual(e.response_content, error_dict)
            self.assertIsNotNone(e.response_headers)

    @aioresponses()
    async def test_get_mail_simulating_500(self, mocked_res):
        i = self.get_instance()

        url = "https://graph.microsoft.com/v1.0/users/uid/messages/mid"
        mocked_res.get(url, status=500, headers={"Content-Type": "text/plain"}, body="error".encode())
        try:
            await i.get_mail("uid", "mid", token=TestClient._token)
            self.fail("should raise an exception")
        except InternalServerError as e:
            self.assertEqual(e.request_url, url)
            self.assertEqual(e.status, HTTPStatus.INTERNAL_SERVER_ERROR)
            self.assertEqual(e.response_content, b"error")
            self.assertIsNotNone(e.response_headers)

    async def test_get_mail_as_mime(self):
        i = self.get_instance()

        mail, status = await i.get_mail(
            TestClient._user_id, TestClient._valid_message_id, as_mime=True, token=TestClient._token)

        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(bytes, type(mail))

    async def test_add_extension_to_message_and_delete_it(self):
        i = self.get_instance()

        extension_name = "ScannedByBitDam"
        extension_data = {
            "companyName": "Datto",
            "verdict": "malicious",
            "scanId": "testing_open_extension_scan_id"
        }

        mail, status = await i.add_extension_to_message(
            TestClient._user_id, TestClient._valid_message_id, extension_name=extension_name,
            extension_data=extension_data, token=TestClient._token)

        self.assertEqual(status, HTTPStatus.CREATED)

        odata_query = ODataQuery()
        odata_query.top = TestClient._bulk_size
        odata_query.filter = Filter([Constrain(attribute="Extensions", logical_operator=LogicalOperator.ANY_EQ, value="ScannedByBitDam", inner_attribute="id")])

        res, status = await i.list_user_mails_bulk(
            TestClient._user_id, token=TestClient._token, odata_query=odata_query)
        self.assertEqual(status, HTTPStatus.OK)
        current_with_extensions = len(res["value"])
        self.assertTrue(current_with_extensions > 0)

        mail, status = await i.delete_extension_from_message(
            TestClient._user_id, TestClient._valid_message_id, extension_name=extension_name,
            token=TestClient._token)
        self.assertEqual(status, HTTPStatus.NO_CONTENT)

        res, status = await i.list_user_mails_bulk(
            TestClient._user_id, token=TestClient._token, odata_query=odata_query)
        self.assertEqual(status, HTTPStatus.OK)
        after_delete_with_extensions = len(res["value"])
        self.assertEqual(after_delete_with_extensions, current_with_extensions - 1)

    async def test_send_mail_basic_exceptions(self):
        i = self.get_instance()
        mail = {}
        headers = {}
        attachments = {}
        try:
            _, status = await i.send_mail(
                mail, headers=headers, attachments=attachments, token=TestClient._token)
        except GraphClientException as e:
            self.assertIn("must contain a 'from' email address", e.message)

        mail['from'] = TestClient._mail_from_user
        try:
            _, status = await i.send_mail(
                mail, headers=headers, attachments=attachments, token=TestClient._token)
        except GraphClientException as e:
            self.assertIn("must contain a 'to' list of email", e.message)

        mail['to'] = TestClient._mail_to_users
        try:
            _, status = await i.send_mail(
                mail, headers=headers, attachments=attachments, token=TestClient._token)
        except GraphClientException as e:
            self.assertIn("dict must contain a 'body_content' string", e.message)

        mail['body_content'] = "Test email!"
        headers = {
            'header-one': 'value',
            'header-two': 'value',
            'header-three': 'value',
            'header-four': 'value',
            'header-five': 'value',
            'header-six': 'value'
        }
        try:
            _, status = await i.send_mail(
                mail, headers=headers, attachments=attachments, token=TestClient._token)
        except GraphClientException as e:
            self.assertIn("should be less than or equal to 5", e.message)

        headers.pop('header-six')
        _, status = await i.send_mail(mail, headers=headers, attachments=attachments, token=TestClient._token)
        self.assertEqual(status, HTTPStatus.ACCEPTED)

    async def test_send_mail_with_headers_and_attachment(self):
        i = self.get_instance()
        mail = {
            'to': TestClient._mail_to_users,
            'from': TestClient._mail_from_user,
            'body_content': "<bold>An HTML email!</bold>",
            'body_type': "HTML",
            "save_to_sent_items": True
        }
        headers = {
            'Custom-Header': 'Custom-Value'
        }
        attachments = [{
            'name': "test.txt",
            'contentType': "plain/text",
            'contentBytes': "QSB0ZXN0IGZpbGUgZ29lcyBoZXJlIQ=="
        }]
        _, status = await i.send_mail(
                mail, headers=headers, attachments=attachments, token=TestClient._token)

        self.assertEqual(status, HTTPStatus.ACCEPTED)

    async def test_get_latest_delta_url_user_drive(self):
        i = self.get_instance()

        delta_url = await i.get_latest_delta_link(USERS, TestClient._user_id, token=TestClient._token)

        self.assertIsNotNone(delta_url)

    async def test_list_recent_drive_files(self):
        i = self.get_instance()
        odata_query = ODataQuery()
        odata_query.top = 10
        odata_query.order_by = OrderBy("lastModifiedDateTime", Order.desc)
        wanted = 20
        current = 0
        recent_drive_items = []
        async for drive_item in i.list_recent_files(USERS, TestClient._user_id, token=TestClient._token, odata_query=odata_query):
            if type(drive_item) == dict:
                current += 1
                recent_drive_items.append(drive_item)
            if current == wanted:
                break

        self.assertEqual(len(recent_drive_items), wanted)

    async def test_get_latest_delta_url_site_drive(self):
        i = self.get_instance()

        delta_url = await i.get_latest_delta_link(SITES, TestClient._site_id, token=TestClient._token)

        self.assertIsNotNone(delta_url)

    async def test_get_latest_delta_url_group_drive(self):
        i = self.get_instance()

        delta_url = await i.get_latest_delta_link(GROUPS, TestClient._group_id, token=TestClient._token)

        self.assertIsNotNone(delta_url)

    async def test_get_drive_file_content(self):
        i = self.get_instance()

        drive_item_content, status = await i.get_drive_item_content(
            USERS, TestClient._user_id, TestClient._one_drive_file_id, token=TestClient._one_drive_token)

        self.assertIsNotNone(drive_item_content)
        self.assertEqual(type(drive_item_content), bytes)

    async def test_get_drive_item(self):
        i = self.get_instance()

        drive_item, status = await i.get_drive_item(
            TestClient._remote_drive_id, TestClient._remote_drive_item_id, token=TestClient._one_drive_token)

        self.assertEqual(status, HTTPStatus.OK)
        self.assertIsNotNone(drive_item)
        self.assertEqual(type(drive_item), dict)

    async def test_get_user_drive_item(self):
        i = self.get_instance()

        drive_item, status = await i.get_user_drive_item(
            TestClient._user_id, TestClient._remote_drive_item_id, token=TestClient._one_drive_token)

        self.assertEqual(status, HTTPStatus.OK)
        self.assertIsNotNone(drive_item)
        self.assertEqual(type(drive_item), dict)

    async def test_list_some_user_drive_content_using_iterator(self):
        i = self.get_instance()

        delta_url = await i.get_latest_delta_link(USERS, TestClient._user_id, token=TestClient._token)

        items = []
        async for drive_item in i.list_drive_changes(delta_url, token=TestClient._token):
            if type(drive_item) == dict:
                items.append(drive_item)

    async def test_get_sites(self):
        i = self.get_instance()
        odata = ODataQuery()
        odata.top = 10
        sites = []
        async for site in i.list_all_sites(
                token=TestClient._token_subscription_with_resource_data, odata_query=odata):
            sites.append(site)
        self.assertIsNotNone(sites)

    async def test_get_sites_bulk(self):
        i = self.get_instance()
        odata = ODataQuery()
        odata.top = 2
        res, stauts = await i.list_sites_bulk(token=TestClient._token_subscription_with_resource_data, odata_query=odata)
        self.assertEqual(stauts, HTTPStatus.OK)
        self.assertEqual(len(res["value"]), 2)

    async def test_get_sites_bulk_and_then_list_more(self):
        i = self.get_instance()
        odata = ODataQuery()
        odata.top = 2
        res, stauts = await i.list_sites_bulk(token=TestClient._token_subscription_with_resource_data, odata_query=odata)
        self.assertEqual(stauts, HTTPStatus.OK)
        self.assertEqual(len(res["value"]), 2)

        res, stauts = await i.list_more(
            next_url=res[NEXT_KEY], token=TestClient._token_subscription_with_resource_data, odata_query=odata)

        self.assertEqual(stauts, HTTPStatus.OK)
        self.assertEqual(len(res["value"]), 2)

    async def test_get_groups_bulk(self):
        i = self.get_instance()
        odata = ODataQuery()
        odata.top = 2
        res, stauts = await i.list_groups_bulk(token=TestClient._token_subscription_with_resource_data, odata_query=odata)
        self.assertEqual(stauts, HTTPStatus.OK)
        self.assertEqual(len(res["value"]), 2)

        res, stauts = await i.list_more(
            next_url=res[NEXT_KEY], token=TestClient._token_subscription_with_resource_data, odata_query=odata)

        self.assertEqual(stauts, HTTPStatus.OK)
        self.assertEqual(len(res["value"]), 2)

    async def test_list_all_groups(self):
        i = self.get_instance()

        groups_counter = 0
        async for _ in i.list_all_groups(token=TestClient._token_subscription_with_resource_data):
            groups_counter += 1

        self.assertTrue(groups_counter > 0)

    async def test_get_site(self):
        i = self.get_instance()

        res, status = await i.get_site(self._site_id, token=TestClient._token)

        self.assertEqual(HTTPStatus.OK, status)
        self.assertEqual(res["id"], self._site_id)

    async def test_get_group(self):
        i = self.get_instance()

        res, status = await i.get_group(self._group_id, token=TestClient._token)

        self.assertEqual(HTTPStatus.OK, status)
        self.assertEqual(res["id"], self._group_id)

    async def test_get_team(self):
        i = self.get_instance()
        res, status = await i.get_team(TestClient._team_id, token=TestClient._token)

        self.assertEqual(HTTPStatus.OK, status)
        self.assertEqual(res["id"], TestClient._team_id)

    async def test_get_channel(self):
        i = self.get_instance()
        res, status = await i.get_channel(TestClient._team_id, TestClient._channel_id, token=TestClient._token)

        self.assertEqual(HTTPStatus.OK, status)
        self.assertEqual(res["id"], TestClient._channel_id)

    def test_generate_authorization_url(self):
        i = self.get_instance()

        redirect_url = "https://redirect-here.com/a/b"
        state = {"foo": "bla"}

        auth_url = i.generate_authorization_url(TestClient._test_app_id, redirect_url, state)
        parts = list(urllib.parse.urlparse(auth_url))
        self.assertEqual(parts[0], "https")
        self.assertEqual(parts[1], "login.microsoftonline.com")
        self.assertEqual(parts[2], "/common/adminconsent")
        query_params = urllib.parse.unquote_plus(parts[4])
        self.assertTrue('redirect_uri=https://redirect-here.com/a/b' in query_params)
        self.assertTrue('&state={"foo": "bla"}' in query_params)

    def test_mocked_graph_url_consent_flow(self):
        i = self.get_instance(mocked_graph_url="http://my-mocked-msgraph-service.com")

        redirect_url = "https://redirect-here.com/a/b"
        state = {"foo": "bla"}

        auth_url = i.generate_authorization_url(TestClient._test_app_id, redirect_url, state)
        parts = list(urllib.parse.urlparse(auth_url))
        self.assertEqual(parts[0], "http")
        self.assertEqual(parts[1], "my-mocked-msgraph-service.com")
        self.assertEqual(parts[2], "/common/adminconsent")
        query_params = urllib.parse.unquote_plus(parts[4])
        self.assertTrue('redirect_uri=https://redirect-here.com/a/b' in query_params)
        self.assertTrue('&state={"foo": "bla"}' in query_params)

    @aioresponses()
    async def test_get_site_mocked_graph_url(self, mocked_res):
        mocked_base_url = "http://my-mocked-msgraph-service.com"
        i = self.get_instance(mocked_graph_url=mocked_base_url)

        url = f"{mocked_base_url}/v1.0/sites/sid"
        res_dict = {"bla": "bla"}
        mocked_res.get(url, status=500, body=json.dumps(res_dict).encode())

        try:
            await i.get_site("sid", token=TestClient._token)
        except BaseHttpError as e:
            self.assertEqual(e.request_url, url)
