from odoo import models,api

class PosOrder(models.Model):
    _inherit = "pos.order"
    _description = "Sending SMS while creating or refunding order in POS Screen"
    
    
    @api.model
    def _process_order(self, pos_order):
        api_obj=self.env['api.msg91']
        pos_order_result = super(PosOrder, self)._process_order(pos_order)
        sms_template_objs = self.env["sms.template"].sudo().search(
            [('condition', '=', 'order_confirm_pos')])
        for sms_template_obj in sms_template_objs:
            mobile = sms_template_obj._get_partner_mobile(pos_order_result.partner_id)
#            print "mobilemobile",mobile
            if mobile:
                data={
                'message':sms_template_objs.get_body_data(pos_order_result),
                'mobile':mobile,
                'model_id':pos_order_result.id,
                'partner_id':pos_order_result.partner_id.id,
                'model_name':'pos.order',
                }
                
                api_obj.makecall(data)
        return pos_order_result
