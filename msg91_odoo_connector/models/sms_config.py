from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
    
class SMSConfig(models.Model):
    _name='sms.config'
    
    
    name=fields.Char('Name')
    auth_key=fields.Char('AuthKey')
    url=fields.Char('URL')
    route=fields.Char('Route ID',default='default')
    senderid=fields.Char('Sender ID')
    
    @api.multi
    def sms_config_details(self):
        result={
        'auth_key':self.auth_key,
        'url':self.url,
        'route':self.route,
        'senderid':self.senderid,
        }
        return result
