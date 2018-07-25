from odoo import api, fields, models
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class account_invoice(models.Model):
    _inherit = "account.invoice"
    
    landed_costs_id = fields.Many2many('stock.landed.cost', 'invoice_landed_cost_rel', 'invoice_id', 'landed_cost_id', string='Landed Costs')
    is_shipping_company = fields.Boolean(related='partner_id.is_shipping_company',string="Is Shipping Company?")
    
    
    
    @api.onchange('landed_costs_id')
    def _onchange_landed_costs_id(self):
        print('amount_totalamount_total')
        amount_total=0
        self.env.cr.execute("SELECT landed_cost_id FROM invoice_landed_cost_rel")
        landed_cost_ids=self.env.cr.fetchall()
        print('landed_cost_id===',landed_cost_ids)
        landed_cost_id=[landed_cost_id[0] for landed_cost_id in landed_cost_ids]
        print('landed_cost_id----',landed_cost_id)
        for inv in self:
            inv_line_id=inv.invoice_line_ids.filtered(lambda o: o.product_id.landed_cost_ok==True)
            if inv.landed_costs_id:
                for landed_cost_id in inv.landed_costs_id:
                    amount_total+=landed_cost_id.amount_total
            
                print('inv_line_id',inv_line_id)
                if inv_line_id:
                    inv_line_id.write({'price_unit':amount_total})
                else:
                    product_id=self.env['product.product'].search([('landed_cost_ok','=',True)])
                    if product_id:
                        account_id=False
                        if product_id.property_account_expense_id:
                            account_id=product_id.property_account_expense_id.id
                        elif product_id.categ_id:
                            account_id=product_id.categ_id.property_account_expense_categ_id.id
                        vals=({'invoice_id':inv.id,
                            'product_id':product_id.id,
                            'name':product_id.name,
                            'product_id':product_id.id,
                            'account_id':account_id,
                            'quantity':1,
                            'price_unit':amount_total,

                            })
                        print('vals====',vals)
                    inv.invoice_line_ids+=self.env['account.invoice.line'].new(vals)
#            if not inv.landed_costs_id:
#                
#                print('inv_line_id===else',inv_line_id)
#                inv_line_id.unlink()
#                inv.landed_costs_id.unlink()
        domain={'landed_costs_id':[('id','not in',landed_cost_id)]}
        return {'domain':domain}
                            