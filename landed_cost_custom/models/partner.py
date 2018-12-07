from odoo import api, fields, models
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"
    
    is_shipping_company = fields.Boolean(string="Is Shipping Company?")

    