This is a client for Microsoft Graph API

The client currently supports the following Graph API:
* Acquiring access token
* Generating authorization url for admin consent
* Users basic operations (list/get)
* Subscriptions operations (create/renew/delete, also for chat resources)
* Mails operations (list/get/send/add and remove open extensions)
* SharePoint sites operations (list/get)
* Drive resources operations (get delta link/list changes)
* Groups operations (list/get)
* Teams operations (get)
* Channels operations (get)


The client is async, meaning all functions are awaitable.

The client supports automatic token refresh, this is done by calling `manage_token` passing it app-id, app-secret and tenant-id.

If token is managed, then there's no need to pass the token to any of the client call.
However, if the token is not managed, you will need to provide it with every call as part of kwargs (e.g. `list_users(token="your access token here")`).

This client is intended to serve tenant-admin so there's currently no user-context api.
