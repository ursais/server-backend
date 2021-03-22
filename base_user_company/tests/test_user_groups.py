# Copyright 2014 ABF OSIELL <http://osiell.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import datetime

from odoo import fields
from odoo.tests.common import TransactionCase


class TestUserGroups(TransactionCase):
    def setUp(self):
        super().setUp()

        self.company_A = self.env.ref("base.main_company")
        self.company_B = self.env["res.company"].create({"name": "Company B"})

        User = self.env["res.users"]
        self.user_test = User.create(
            {
                "name": "Test User",
                "login": "test_user",
                "company_ids": [(6, 0, [self.company_A.id, self.company_B.id])],
            }
        )

        Group = self.env["res.groups"]
        self.group_A = Group.create(
            {
                "name": "Group A",
                "company_id": self.company_A.id,
                "users": [(6, 0, [self.user_test.id])],
            }
        )
        self.group_B = Group.create(
            {
                "name": "Group B",
                "company_id": self.company_B.id,
                "users": [(6, 0, [self.user_test.id])],
            }
        )

        self.test_record = self.user_test.with_user(self.user_test)

    def test_group_company(self):
        a_record = self.test_record.with_company(self.company_B)
        group_B_xmlid = self.group_B.__ensure_xml_id()
        import pudb; pu.db
        self.assertFalse(
            a_record.has_group(group_B_xmlid),
            "With Company B the Group A must not be active",
        )
