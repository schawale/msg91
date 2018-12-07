from odoo import api, models, fields, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    amount_resisual = fields.Float('Residual amount', readonly=True,
                                   compute="_get_amount_residual",store=True)

    
    def get_num2words_amount(self, amount):
       amt_word=self.company_id.currency_id.amount_to_text(float(amount))
       return amt_word 
   
    #get extra row in report
    @api.multi
    def get_extra_rows(self,lines):
        if lines< self.company_id.sale_line:
            counter=0
            rows=""
            while counter!=(self.company_id.sale_line):
                rows+="<tr style='border:none;'>"
                for each in range(0,5):
                    if each==0:
                        rows+="<td height='20px' style='border;none;border-right:1px dotted;border-left:none;'></td>"
                    elif each==4:
                        rows+="<td height='20px' style='border:none;border-left:1px dotted;'></td>"
                    else:
                        rows+="<td height='20px' style='border:none;border-right:1px dotted;border-left:1px dotted;'></td>"
                rows+="</tr>"
                counter +=1
            return rows
