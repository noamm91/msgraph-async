from enum import Enum

GRAPH_BASE_URL = "https://graph.microsoft.com"
V1_EP = "/v1.0"
BETA_EP = "/beta"

# OData query params
SELECT = "$select"
COUNT = "$count"
FILTER = "$filter"
SEARCH = "search"

# Resources
USERS = "/users"
SUBSCRIPTIONS = "/subscriptions"
MAILS = "/messages"

# next_key
NEXT_KEY = "@odata.nextLink"


# Subscription Resources
class SubscriptionResourcesTemplates(Enum):
    Mailbox             = "Users('{}')/messages"
    Inbox               = "Users('{}')/mailFolders('Inbox')/messages"
    DriveRoot           = "users/{}/drive/root"
    SiteDocumentLibrary = "sites/{}/drive/root"
    GroupDriveRoot      = "groups/{}/drive/root"
    TenantTeamsChannels = "teams/allMessages"
    TenantChats         = "chats/allMessages"
