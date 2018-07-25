from odoo import models,api

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    _description = "Sending SMS while Validating Invoice"
    
    @api.multi
    def invoice_validate(self):
        mobile=False
        api_obj=self.env['api.msg91']
        invoice_result = super(AccountInvoice, self).invoice_validate()
        sms_template_objs = self.env["sms.template"].sudo().search(
                [('condition', '=', 'invoice_vaildate')])
        print ("sms_template_objssms_template_objs",sms_template_objs)
        for sms_template_obj in sms_template_objs:
            mobile = self.partner_id.mobile
            print ("mobilemobile",mobile)
            if mobile:
                data={
                'message':sms_template_objs.get_body_data(self),
                'mobile':mobile,
                'model_id':self.id,
                'partner_id':self.partner_id.id,
                'model_name':'account.invoice',
                }

                api_obj.makecall(data)
        return invoice_result

                   
