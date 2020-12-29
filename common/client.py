import typing
import aiohttp
import json
import asyncio
from .constants import *


class SimpleGraphClient:

    def __init__(self):
        self.session = aiohttp.ClientSession()

    @staticmethod
    def build_url(version, resource, odata_params):
        url = GRAPH_BASE_URL + version + resource
        if odata_params:
            url += "?"
        for param in odata_params:
            url += param
        return url

    @staticmethod
    def build_auth_header(token: str):
        if token.lower().startswith("bearer"):
            return {"authorization": token}
        else:
            return {"authorization": f"bearer {token}"}

    async def get_users(self, token: str, search=None, count=None, filter=None, select=None) -> typing.List[typing.Dict]:
        url = self.build_url(V1_EP, USERS, [])
        headers = self.build_auth_header(token)
        async with self.session.get(url, headers=headers) as resp:
            status = resp.status
            payload: str = resp.text()
        if status == 200:
            return json.load(payload)["value"]
