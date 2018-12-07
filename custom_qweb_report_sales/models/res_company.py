from odoo import models, fields, api

class ResCompany(models.Model):
    
    _inherit = "res.company"
    
    sale_line = fields.Integer('Invoice Line')