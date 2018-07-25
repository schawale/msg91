from odoo import models,api,fields
import re

class SmsTemplate(models.Model):
    "Templates for sending sms"
    _name = "sms.template"
    _description = 'SMS Templates'
    _order = 'name'
    
    
    def _get_partner_mobile(self, partner):
        print ("partner---------------",partner)
        return partner.mobile
    
    
    @api.multi
    def get_body_data(self, obj):
        self.ensure_one()
        if obj:
            if 'res.partner' in self.model:
                obj.partner_id=obj
            body_msg = self.env["mail.template"].with_context(lang=obj.partner_id.lang).sudo().render_template(
                self.sms_body_html, self.model, [obj.id])
            new_body_msg = re.sub("<.*?>", " ", body_msg[obj.id])
            return new_body_msg
            return " ".join(strip_tags(new_body_msg).split())
    
    
    @api.depends('condition')
    def onchange_condition(self):
        if self.condition:
            if self.condition in ['order_placed', 'order_confirm', 'order_cancel']:
                model_id = self.env['ir.model'].search(
                    [('model', '=', 'sale.order')])
                self.model_id = model_id.id if model_id else False
            elif self.condition in ['order_delivered']:
                model_id = self.env['ir.model'].search(
                   [('model', '=', 'stock.picking')])
                self.model_id = model_id.id if model_id else False
            elif self.condition in ['invoice_vaildate', 'invoice_paid']:
                model_id = self.env['ir.model'].search(
                    [('model', '=', 'account.invoice')])
                self.model_id = model_id.id if model_id else False
            elif self.condition in ['order_refund_pos','order_confirm_pos']:
                model_id = self.env['ir.model'].search(
                    [('model', '=', 'pos.order')])
                self.model_id = model_id.id if model_id else False
            elif self.condition in ['pos_partner_create']:
                model_id = self.env['ir.model'].search(
                    [('model', '=', 'res.partner')])
                self.model_id = model_id.id if model_id else False
        else:
            self.model_id = False
    active = fields.Boolean(string="Active", default=True)
    name = fields.Char('Name', required=True)
    auto_delete = fields.Boolean("Auto Delete")
    globally_access = fields.Boolean(
        string="Global", help="if enable then it will consider normal(global) template.You can use it while sending the bulk message. If not enable the you have to select condition on which the template applies.")
    model_id = fields.Many2one(
        'ir.model', 'Applies to', compute="onchange_condition", help="The kind of document with this template can be used. Note if not selected then it will consider normal(global) template.", store=True)
    model = fields.Char(related="model_id.model", string='Related Document Model',
                        store=True, readonly=True)
    sms_body_html = fields.Text('Body', translate=True, sanitize=False,
                                help="SMS text. You can also use ${object.partner_id} for dynamic text. Here partner_id is a field of the document(obj/model).", )

    condition = fields.Selection([('order_placed', 'Order Placed'),
                                  ('order_confirm', 'Order Confirmed'),
                                  ('order_confirm_pos', 'Order Confirmed POS'),
                                  ('order_refund_pos', 'Order Refund POS'),
                                  ('pos_partner_create', 'POS Partner Creation'),
                                  ('order_delivered', 'Order Delivered'),
                                  ('invoice_vaildate', 'Invoice Validate'),
                                  ('invoice_paid', 'Invoice Paid'),
                                  ('order_cancel', 'Order Cancelled')], string="Conditions", help="Condition on which the template has been applied.")
