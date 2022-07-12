This is a client for Microsoft Graph API

The client currently supports the following Graph API:
* Acquiring access token
* Generating authorization url for admin consent
* Users basic operations (list/get)
* Subscriptions operations (create/renew/delete, also for chat resources)
* Mails operations (list/get/send/add/delete/attachments/extensions/user-purpose)
* Mail folders operations (get-bulk/get/list)
* SharePoint sites operations (list/get)
* Drive resources operations (get delta link/list changes/list recent changes/get (by user, by drive))
* Groups operations (list/get)
* Teams operations (get)
* Channels operations (get)
* Domains operations (list/get)
* Service Principals operations (list/get)

The client is async, meaning all functions are awaitables.

Odata query is also generally supported, you can build the query and pass it to any supported function as key-word argument

The client supports automatic token refresh, this is done by calling `manage_token` passing it app-id, app-secret and tenant-id.

If token is managed, then there's no need to pass the token to any of the client call.
However, if the token is not managed, you will need to provide it with every call as part of kwargs (e.g. `list_users(token="your access token here")`).

This client is intended to serve tenant-admin so the only user-context api that is currently supported is to acquire access token from refresh token.
