import unittest

from app.api.dao.user import UserDAO
from tests.base_test_case import BaseTestCase


class TestUpdateUserDao(BaseTestCase):
    def test_dao_update_user(self):

        self.assertIsNone(self.admin_user.occupation)
        self.assertIsNone(self.admin_user.current_organization)

        data = dict(occupation="good_developer", current_organization="good_org")
        UserDAO.update_user_profile(self.admin_user.id, data)

        self.assertEqual("good_developer", self.admin_user.occupation)
        self.assertEqual("good_org", self.admin_user.current_organization)

    def test_update_fields_with_empty_data(self):

        self.assertIsNone(self.admin_user.occupation)
        self.assertIsNone(self.admin_user.current_organization)

        data = dict(occupation="good_developer", current_organization="good_org")
        UserDAO.update_user_profile(self.admin_user.id, data)

        self.assertEqual("good_developer", self.admin_user.occupation)
        self.assertEqual("good_org", self.admin_user.current_organization)

        data = dict(occupation="", current_organization="")
        UserDAO.update_user_profile(self.admin_user.id, data)

        self.assertIsNone(self.admin_user.occupation)
        self.assertIsNone(self.admin_user.current_organization)


if __name__ == "__main__":
    unittest.main()
