import typing
import logging
import json
import aiohttp
from base64 import b64encode
from msgraph_async.common.constants import *
from msgraph_async.common.exceptions import *
from msgraph_async.common.odata_query import *
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from functools import wraps


def authorized(func):
    @wraps(func)
    def actual(*args, **kwargs):
        client: GraphAdminClient = args[0]
        if not client._token and not kwargs.get("token"):
            raise Exception('Token is not managed so you must explicitly provide it')

        token = kwargs["token"] if kwargs.get("token") else client._token
        kwargs["_req_headers"]: dict = client._build_auth_header(token)
        kwargs["_req_headers"].update({"Content-type": "application/json"})
        if kwargs.get("extra_headers"):
            kwargs["_req_headers"].update(kwargs["extra_headers"])
        return func(*args, **kwargs)

    return actual


class GraphAdminClient:

    def __init__(self, enable_logging=False):
        self._session = aiohttp.ClientSession()
        self._token = None
        self._managed = False
        self._token_refresh_interval_sec = 3300
        self._scheduler = AsyncIOScheduler()
        self._enable_logging = enable_logging

    @property
    def token_refresh_interval_sec(self):
        return self._token_refresh_interval_sec

    @token_refresh_interval_sec.setter
    def token_refresh_interval_sec(self, value):
        if value < 60 or value > 3600:
            raise ValueError("refresh interval must be between 60 and 3600 seconds")
        self._token_refresh_interval_sec = value

    @property
    def is_managed(self):
        return self._managed

    @property
    def token(self):
        return self._token

    @staticmethod
    def _build_url(version, resources: typing.List[typing.Tuple], **kwargs):
        url = GRAPH_BASE_URL + version
        for resource, resource_id in resources:
            url += resource
            if resource_id:
                url += f"/{resource_id}"

        odata_query: ODataQuery = kwargs.get("odata_query")
        if odata_query:
            url += str(odata_query)

        if kwargs.get("_value_query_param"):
            url += "/$value"

        return url

    @staticmethod
    def _build_auth_header(token: str):
        if token.lower().startswith("bearer"):
            return {"authorization": token}
        else:
            return {"authorization": f"bearer {token}"}

    @staticmethod
    def _get_resource(resource_template: SubscriptionResources, resource_id):
        return resource_template.value.format(resource_id)

    @staticmethod
    def _get_msgraph_time_format(minutes_to_expiration: int):
        val = (datetime.utcnow() + timedelta(minutes=minutes_to_expiration)).strftime("%Y-%m-%dT%H:%M:%S.%f") + "0Z"
        return val

    def _log(self, level, msg):
        if self._enable_logging:
            logging.log(level, msg)

    async def _refresh_token(self, app_id, app_secret, tenant_id):
        content, status_code = await self.acquire_token(app_id, app_secret, tenant_id)
        self._token = content['access_token']
        self._log(logging.INFO, "token has been refreshed")

    async def _request(self, method, url, headers: dict = None, data: dict = None, expected_statuses=None):
        if not expected_statuses:
            expected_statuses = (HTTPStatus.OK, HTTPStatus.NO_CONTENT, HTTPStatus.CREATED)
        try:
            async with self._session.request(method, url, headers=headers, data=data) as resp:
                status = resp.status
                resp_headers = resp.headers
                if resp.headers.get('Content-Type') and 'application/json' in resp.headers['Content-Type']:
                    r: dict = await resp.json()
                else:
                    r: bytes = await resp.read()

            if status in expected_statuses:
                return r, status
            else:
                raise status2exception.get(status, UnknownError)(status, url, r, resp_headers)
        except Exception as e:
            self._log(logging.ERROR, f"exception while making a request: {str(e)}")
            raise e

    async def acquire_token(self, app_id, app_secret, tenant_id):
        """
        Get token from Microsoft
        :param app_id: Also called client id, the identifier of your application in Azure,
        consent must have been granted in order to success
        :param app_secret: Secret of your application in Azure
        :param tenant_id: Id of the tenant you're asking access to its' resources
        :return: Dictionary with token data
        """
        req_body = {
            "grant_type": "client_credentials",
            "scope": "https://graph.microsoft.com/.default",
            "client_id": app_id,
            "client_secret": app_secret,
        }
        url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        content, status = await self._request("POST", url, data=req_body)
        return content, status

    async def manage_token(self, app_id, app_secret, tenant_id):
        """
        Let the client keep a valid token for you.
        The client will refresh it (i.e. acquire new one) every token_refresh_interval_sec.
        If the token is managed, then you don't need to provide it in every request.
        :param app_id: app_id: Also called client id, the identifier of your application in Azure,
        consent must have been granted in order to success
        :param app_secret: Secret of your application in Azure
        :param tenant_id: Id of the tenant you're asking access to its' resources
        :return: None if the operation was successful, else - raises GraphClientException with info
        """
        if self._managed:
            raise GraphClientException("Token is already managed")
        try:
            await self._refresh_token(app_id, app_secret, tenant_id)
            self._scheduler.add_job(self._refresh_token, 'interval', args=[app_id, app_secret, tenant_id],
                                    seconds=self._token_refresh_interval_sec)
            self._scheduler.start()
            self._managed = True
        except Exception as e:
            self._log(logging.ERROR, f"exception while trying to set manage token: {str(e)}")
            raise GraphClientException(e)

    @authorized
    async def get_user(self, user_id, **kwargs):
        """
        Get user by its' ID
        :param user_id: thd ID of the user
        :param
        :return:
        """
        url = self._build_url(V1_EP, [(USERS, user_id)], **kwargs)
        res, status = await self._request(
            "GET", url, kwargs["_req_headers"], expected_statuses=kwargs.get("expected_statuses"))
        return res, status

    @authorized
    async def list_users_bulk(self, **kwargs):
        url = self._build_url(V1_EP, [(USERS, None)], **kwargs)
        res, status = await self._request("GET", url, kwargs["_req_headers"],
                                          expected_statuses=kwargs.get("expected_statuses"))
        return res, status

    @authorized
    async def list_more_users(self, next_url, **kwargs):
        res, status = await self._request("GET", next_url, kwargs["_req_headers"],
                                          expected_statuses=kwargs.get("expected_statuses"))
        return res, status

    @authorized
    async def list_all_users(self, **kwargs):
        res, status = await self.list_users_bulk(**kwargs)
        next_url = res.get(NEXT_KEY)
        for user in res["value"]:
            yield user
        while next_url:
            res, status = await self.list_more_users(next_url, **kwargs)
            next_url = res.get(NEXT_KEY)
            for user in res["value"]:
                yield user

    @authorized
    async def create_subscription(
            self, change_type: str, notification_url: str, resource: SubscriptionResources, minutes_to_expiration: int,
            client_state: str = None, latest_supported_tls_version: str = None, user_id: str = None,
            life_cycle_url: str = None, plain_certificate: str = None, **kwargs):

        if not resource.resource_data_included:
            if not user_id:
                raise GraphClientException(f"user id must be specified with resource '{resource.name}'")
            resource_str = self._get_resource(resource, user_id)
            body = {}
            url = self._build_url(V1_EP, [(SUBSCRIPTIONS, None)])
        else:
            if not (life_cycle_url and plain_certificate):
                raise GraphClientException(f"life cycle url and certificate must be specified with resource ({resource.name})")
            resource_str = resource.value

            b64_certificate = b64encode(plain_certificate.encode()).decode()

            body = {
                "includeResourceData": True,
                "lifecycleNotificationUrl": life_cycle_url,
                "encryptionCertificate": b64_certificate,
                "encryptionCertificateId": "CertificateId"
            }
            url = self._build_url(BETA_EP, [(SUBSCRIPTIONS, None)])

        expiration_date_time = self._get_msgraph_time_format(minutes_to_expiration)

        body.update({
            "changeType": change_type,
            "notificationUrl": notification_url,
            "resource": resource_str,
            "expirationDateTime": expiration_date_time,
            "clientState": "secretClientValue"
        })
        if client_state:
            body["clientState"] = client_state

        if latest_supported_tls_version:
            body["latestSupportedTlsVersion"] = latest_supported_tls_version

        res, status = await self._request("POST", url, kwargs["_req_headers"], json.dumps(body), kwargs.get("expected_statuses"))
        return res, status

    @authorized
    async def renew_subscription(self, subscription_id: str, resource: SubscriptionResources,
                                 minutes_to_expiration: int, **kwargs):
        if not resource.resource_data_included:
            url = self._build_url(V1_EP, [(SUBSCRIPTIONS, subscription_id)])
        else:
            url = self._build_url(BETA_EP, [(SUBSCRIPTIONS, subscription_id)])

        expiration_date_time = self._get_msgraph_time_format(minutes_to_expiration)
        body = {
            "expirationDateTime": expiration_date_time
        }

        res, status = await self._request("PATCH", url, kwargs["_req_headers"], json.dumps(body),
                                          kwargs.get("expected_statuses"))
        return res, status

    @authorized
    async def delete_subscription(self, subscription_id: str, resource: SubscriptionResources, **kwargs):
        if not resource.resource_data_included:
            url = self._build_url(V1_EP, [(SUBSCRIPTIONS, subscription_id)])
        else:
            url = self._build_url(BETA_EP, [(SUBSCRIPTIONS, subscription_id)])

        res, status = await self._request(
            "DELETE", url, kwargs["_req_headers"], expected_statuses=kwargs.get("expected_statuses"))
        return res, status

    @authorized
    async def list_user_mails_bulk(self, user_id, **kwargs):
        url = self._build_url(V1_EP, [(USERS, user_id), (MAILS, None)], **kwargs)
        res, status = await self._request("GET", url, kwargs["_req_headers"],
                                          expected_statuses=kwargs.get("expected_statuses"))
        return res, status

    @authorized
    async def list_more_user_mails(self, next_url, **kwargs):
        res, status = await self._request("GET", next_url, kwargs["_req_headers"],
                                          expected_statuses=kwargs.get("expected_statuses"))
        return res, status

    @authorized
    async def list_all_user_mails(self, user_id, **kwargs):
        res, status = await self.list_user_mails_bulk(user_id, **kwargs)
        next_url = res.get(NEXT_KEY)
        for mail in res["value"]:
            yield mail
        while next_url:
            res, status = await self.list_more_user_mails(next_url, **kwargs)
            next_url = res.get(NEXT_KEY)
            for mail in res["value"]:
                yield mail

    @authorized
    async def get_mail(self, user_id, message_id, as_mime=False, **kwargs):
        if as_mime:
            kwargs["_value_query_param"] = True
        url = self._build_url(V1_EP, [(USERS, user_id), (MAILS, message_id)], **kwargs)
        res, status = await self._request("GET", url, kwargs["_req_headers"],
                                          expected_statuses=kwargs.get("expected_statuses"))
        return res, status

    @authorized
    async def move_mail(self):
        pass

    @authorized
    async def list_drive_changes(self, state_link: str, **kwargs):
        """

        :param state_link: deltaLink or nextLink, returned from previous calls
        :return: list of drive items changes since state_link was issued
        """
        res, status = await self._request("GET", state_link, kwargs["_req_headers"],
                                          expected_statuses=kwargs.get("expected_statuses"))
        next_url = res.get(NEXT_KEY)
        delta_url = res.get(DELTA_KEY)
        for drive_item in res["value"]:
            yield drive_item
        while next_url:
            res, status = await self.list_drive_changes(next_url, **kwargs)
            next_url = res.get(NEXT_KEY)
            delta_url = res.get(DELTA_KEY)
            for drive_item in res["value"]:
                yield drive_item
        if not delta_url:
            raise GraphClientException("missing deltaLink after iterating through all drive items")
        yield delta_url

    @authorized
    async def get_latest_delta_link(self, resource, id: str, **kwargs) -> str:
        """

        :param resource:
        :param id:
        :param kwargs:
        :return:
        """
        supported_drive_resources = [USERS, SITES, GROUPS]
        if resource not in supported_drive_resources:
            raise GraphClientException(
                f"getting delta url only available for the resources: {supported_drive_resources}")
        drive_delta_url = self._build_url(V1_EP, [(resource, id), (DRIVE, None), ("/root", None)]) + "/delta?token=latest"

        last_value = None
        async for value in self.list_drive_changes(drive_delta_url, **kwargs):
            last_value = value
        return last_value

    @authorized
    async def get_drive_item_content(self, resource, id: str, drive_item_id: str, **kwargs):
        supported_drive_resources = [USERS, SITES, GROUPS]
        if resource not in supported_drive_resources:
            raise GraphClientException(
                f"getting drive file only available for the resources: {supported_drive_resources}")
        url = self._build_url(V1_EP, [(resource, id), (DRIVE, None), ("/items", drive_item_id), ("/content", None)])
        res, status = await self._request("GET", url, kwargs["_req_headers"],
                                          expected_statuses=kwargs.get("expected_statuses"))
        return res, status
