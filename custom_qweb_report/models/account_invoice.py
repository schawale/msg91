from odoo import api, models, fields, _
from num2words import num2words

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    def get_num2words_amount(self, amount):
        amt_word = num2words(amount, lang='en_IN')
        amt_word = str(amt_word).title()
        return amt_word + ' Only'
    
    #get extra row in report
    @api.multi
    def get_extra_rows(self,lines):
        if lines< self.company_id.inv_line:
            counter=0
            rows=""
            while counter!=(self.company_id.inv_line):
                rows+="<tr style='border:1px solid black;'>"
                for each in range(0,5):
                    rows+="<td height='20px' style='border:1px solid black'></td>"
                rows+="</tr>"
                counter +=1
            return rows