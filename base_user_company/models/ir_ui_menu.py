from odoo import api, models, tools


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    @tools.ormcache_context('self._uid', 'debug', keys=('lang', 'company_id'))
    def load_menus(self, debug):
        """
        When switching companies
        """
        menu_root = super().load_menus(debug)
        return menu_root
