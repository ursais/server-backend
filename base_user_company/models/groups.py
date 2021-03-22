# Copyright 2014 ABF OSIELL <http://osiell.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class Groups(models.Model):
    _inherit = "res.groups"

    company_id = fields.Many2one("res.company")
