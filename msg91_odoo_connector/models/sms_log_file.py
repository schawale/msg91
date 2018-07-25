from odoo import api, fields, models, _

class SmsLogFile(models.Model):
    _name='sms.log'
    _rec_name='response_code'
    
    response_code=fields.Char('Response')
    model_id=fields.Integer('ID')
    partner_id=fields.Many2one('res.partner', "Partner")
    model_name = fields.Char(string='Document Model',readonly=True)
SmsLogFile()