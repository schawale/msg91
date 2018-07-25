from odoo import models,api

class AccountPayment(models.Model):
    _inherit = "account.payment"
    _description = "Sending SMS while Paying Invoice"
    
    @api.multi
    def action_validate_invoice_payment(self):
        print ("action_validate_invoice_paymentaction_validate_invoice_payment",self._context)
        active_ids=self._context.get('active_ids')
        invoice_obj=self.env['account.invoice']
        inv_brw=invoice_obj.browse(active_ids)
        mobile=False
        api_obj=self.env['api.msg91']
        invoice_pay_result = super(AccountPayment, self).action_validate_invoice_payment()
        sms_template_objs = self.env["sms.template"].sudo().search(
                [('condition', '=', 'invoice_paid')])
        print ("sms_template_objssms_template_objs",sms_template_objs)
        for sms_template_obj in sms_template_objs:
            mobile = inv_brw.partner_id.mobile
            print ("mobilemobile",mobile)
            if mobile:
                data={
                'message':sms_template_objs.get_body_data(inv_brw),
                'mobile':mobile,
                'model_id':inv_brw.id,
                'partner_id':inv_brw.partner_id.id,
                'model_name':'account.payment',
                }

                api_obj.makecall(data)
        return invoice_pay_result

                   
