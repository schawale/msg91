from odoo import models,api

class SaleOrder(models.Model):
    _inherit = "sale.order"
    _description = "Sending SMS while Confirming a Sale Order"
    
    @api.multi
    def action_confirm(self):
        mobile=False
        api_obj=self.env['api.msg91']
        sale_result = super(SaleOrder, self).action_confirm()
        sms_template_objs = self.env["sms.template"].sudo().search(
            [('condition', '=', 'order_confirm')])
        for sms_template_obj in sms_template_objs:
            mobile = self.partner_id.mobile
        print ("mobilemobile",mobile)
        if mobile:
            data={
            'message':sms_template_objs.get_body_data(self),
            'mobile':mobile,
            'model_id':self.id,
            'partner_id':self.partner_id.id,
            'model_name':'sale.order',
            }

            api_obj.makecall(data)
        return sale_result

                   
