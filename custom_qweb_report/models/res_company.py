from odoo import models, fields, api

class ResCompany(models.Model):
    
    _inherit = "res.company"
    
    bank_name = fields.Char('Bank Name')
    bank_ifcode = fields.Char('Bank IFCS Code')
    inv_line = fields.Integer('Invoice Line')