This is a client for Microsoft Graph API

The client currently supports the following Graph API:
1. Acquiring access token
2. List users
3. Get user
4. Create Subscription
5. Renew Subscription
6. Delete Subscription

The client is async, meaning all functions are awaitable.

The client supports automatic token refresh, this is done by calling `manage_token` passing it app-id, app-secret and tenant-id.

If token is managed, then there's no need to pass it to any of the client call.
However, if the token is not managed, you will need to provide it with every call as part of kwargs (e.g. list_users(token="your access token here").
