## Introduction & Examples

The purpose of this package is to provide an easy to use, async client for Microsoft Graph API.
At this moment, the client is more of an "Admin-Client", that means that it's not in the context of a single user rather of an external tool, operating over some tenants.

In order to use the package you will have to install it:

`pip install msgraph-async`

and then `import` the client and create an instance:

``from msgraph_async import GraphAdminClient`
client = GraphAdminClient()``

### Working with Tokens

In order make a requests to Graph API, you will need an access token.
`msgraph_async` provide you with 2 ways of working with tokens:
1. Manual - you will have to call `acquire_token` and then provide the `token`for every API call:
```
token_info, status = client.acquire_token(YOUR_APP_ID, YOUR_APP_SECRET, TARGET_TENANT_ID)
my_token = token_info["access_token]
client.list_users(token=my_token)
```
Please note that in this scenario, you are responsible for the token.
That means, you will have to acquire new one once it's expired.
If you wish to avoid managing the token yourself, consider using the second option.

2. Managed - you will have to call `manage_token` once, and that's it.
```
client.manage_token(YOUR_APP_ID, YOUR_APP_SECRET, TARGET_TENANT_ID)
client.list_users()
```
Please note the advantages of having a managed token:
1. You don't need to pass it to every API call
2. You don't need to acquire new one near expiration, the client takes care of it for you.


