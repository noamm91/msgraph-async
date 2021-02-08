import unittest
from msgraph_async.common.constants import SubscriptionResources


class TestODataQuery(unittest.TestCase):

    def setUp(self):
        self._user_id = "my_user_id"

    @classmethod
    def setUpClass(cls):
        pass

    def test_inbox_resource(self):
        i = SubscriptionResources.Inbox
        filled = i.value.format(self._user_id)
        self.assertEqual(i.resource_data_included, False)
        self.assertEqual(filled, f"users('{self._user_id}')/mailFolders('Inbox')/messages")

    def test_mail_box_resource(self):
        i = SubscriptionResources.Mailbox
        filled = i.value.format(self._user_id)
        self.assertEqual(i.resource_data_included, False)
        self.assertEqual(filled, f"users('{self._user_id}')/messages")

    def test_drive_root_resource(self):
        i = SubscriptionResources.DriveRoot
        filled = i.value.format(self._user_id)
        self.assertEqual(i.resource_data_included, False)
        self.assertEqual(filled, f"users/{self._user_id}/drive/root")

    def test_site_resource(self):
        i = SubscriptionResources.SiteDocumentLibrary
        filled = i.value.format(self._user_id)
        self.assertEqual(i.resource_data_included, False)
        self.assertEqual(filled, f"sites/{self._user_id}/drive/root")

    def test_groups_drive_root_resource(self):
        i = SubscriptionResources.GroupDriveRoot
        filled = i.value.format(self._user_id)
        self.assertEqual(i.resource_data_included, False)
        self.assertEqual(filled, f"groups/{self._user_id}/drive/root")

    def test_tenant_teams_channels(self):
        i = SubscriptionResources.TenantTeamsChannels
        self.assertEqual(i.resource_data_included, True)
        self.assertEqual(i.value, "teams/allMessages")

    def test_tenant_chats_all_messages(self):
        i = SubscriptionResources.TenantChats
        self.assertEqual(i.resource_data_included, True)
        self.assertEqual(i.value, "chats/allMessages")

