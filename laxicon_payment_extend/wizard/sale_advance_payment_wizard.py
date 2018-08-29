# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import odoo.addons.decimal_precision as dp


class AccountVoucherWizard(models.TransientModel):

    _name = "account.voucher.wizard"

    journal_id = fields.Many2one('account.journal', 'Journal', required=True)
    amount_total = fields.Float('Amount total', readonly=True)
    amount_advance = fields.Float('Amount advanced', required=True,
                                  digits=dp.get_precision('Product Price'))
    date = fields.Date("Date", required=True,
                       default=fields.Date.context_today)
    exchange_rate = fields.Float("Exchange rate", digits=(16, 6), default=1.0,
                                 readonly=True)
    currency_id = fields.Many2one("res.currency", "Currency", readonly=True)
    currency_amount = fields.Float("Curr. amount", digits=(16, 2),
                                   readonly=True)
    payment_ref = fields.Char("Ref.")
    payment_type_mode = fields.Selection([('cheque', 'Cheque'), ('draft', 'Draft'), ('rtgs', 'RTGS'), ('neft', 'NEFT'), ('cash', 'Cash')], string='Payment mode', 
                                         track_visibility='onchange')
    is_account_pay = fields.Boolean(string="A/C pay ?", default=False, track_visibility='onchange' )
    cheque_payee_name = fields.Char(string='Cheque Payer Name', track_visibility='onchange')
    cheque_date = fields.Date(string='Cheque Date', track_visibility='onchange')
    dd_date = fields.Date(string='D.D. Date', track_visibility='onchange' )
    transaction_date = fields.Date(string='Transaction Date', track_visibility='onchange' )
    cheque_number = fields.Char(string='Cheque Number', track_visibility='onchange')
    journal_name = fields.Char(string='journal name')
    bank_id = fields.Many2one('res.bank', string="Company Bank Name", track_visibility='onchange')
    acc_no = fields.Many2one('res.partner.bank', string="Company Account No", track_visibility='onchange')
    transaction_number = fields.Char(string="Transaction ID", track_visibility='onchange')
    dd_number = fields.Char(string="D.D. Number", track_visibility='onchange')
    cust_bank_name = fields.Many2one('bank.payment.cheque', string="Customer Bank Name", track_visibility='onchange')
    cash_payee_name = fields.Char(string="Payer Name", track_visibility="onchange")
    
    @api.onchange('bank_id', 'tra_bank_id')
    def onchange_bank_id(self):
        bank_id = self.bank_id
        order = self.env["sale.order"].\
                browse(self.env.context['active_id'])
        if bank_id:
            acc_list = []
            acc_ids = self.env['res.partner.bank'].search([('bank_id', '=', bank_id.id)])
            if acc_ids:    
                return {'domain': {'acc_no': [('id', 'in', [record.id for record in acc_ids])]}}
    @api.onchange('journal_id')
    def onchange_journal(self):
        if self.journal_id:
            self.journal_name = self.journal_id.type
            self.payment_type_mode = ''
    
    @api.constrains('amount_advance')
    def check_amount(self):
        if self.amount_advance <= 0:
            raise exceptions.ValidationError(_("Amount of advance must be "
                                               "positive."))
        if self.env.context.get('active_id', False):
            order = self.env["sale.order"].\
                browse(self.env.context['active_id'])
            if self.amount_advance > order.amount_resisual:
                raise exceptions.ValidationError(_("Amount of advance is "
                                                   "greater than residual "
                                                   "amount on sale"))

    @api.model
    def default_get(self, fields):
        res = super(AccountVoucherWizard, self).default_get(fields)
        sale_ids = self.env.context.get('active_ids', [])
        if not sale_ids:
            return res
        sale_id = sale_ids[0]

        sale = self.env['sale.order'].browse(sale_id)

        amount_total = sale.amount_resisual

        if 'amount_total' in fields:
            res.update({'amount_total': amount_total,
                        'currency_id': sale.pricelist_id.currency_id.id})

        return res

    @api.onchange('journal_id', 'date')
    def onchange_date(self):
        if self.currency_id:
            self.exchange_rate = 1.0 / \
                (self.env["res.currency"].with_context(date=self.date).
                 _get_conversion_rate(self.currency_id,
                                      (self.journal_id.currency_id or
                                       self.env.user.company_id.
                                       currency_id))
                 or 1.0)
            self.currency_amount = self.amount_advance * \
                (1.0 / self.exchange_rate)
        else:
            self.exchange_rate = 1.0

    @api.onchange('amount_advance')
    def onchange_amount(self):
        self.currency_amount = self.amount_advance * (1.0 / self.exchange_rate)

    @api.multi
    def make_advance_payment(self):
        """Create customer paylines and validates the payment"""
        payment_obj = self.env['account.payment']
        sale_obj = self.env['sale.order']

        sale_ids = self.env.context.get('active_ids', [])
        if sale_ids:
            sale_id = sale_ids[0]
            sale = sale_obj.browse(sale_id)

            partner_id = sale.partner_id.id
            date = self[0].date
            company = sale.company_id

            payment_res = {'payment_type': 'inbound',
                           'partner_id': partner_id,
                           'partner_type': 'customer',
                           'payment_type_mode': self.payment_type_mode,
                           'is_account_pay': self.is_account_pay,
                           'cheque_payee_name': self.cheque_payee_name,
                           'cheque_date': self.cheque_date,
                           'dd_date': self.dd_date,
                           'transaction_date': self.transaction_date,
                           'cheque_number': self.cheque_number,
                           'journal_name': self.journal_name,
                           'bank_id': self.bank_id.id,
                           'acc_no': self.acc_no.id,
                           'transaction_number': self.transaction_number,
                           'dd_number': self.dd_number,
                           'cust_bank_name': self.cust_bank_name.id,
                           'cash_payee_name': self.cash_payee_name,
                           'journal_id': self[0].journal_id.id,
                           'company_id': company.id,
                           'currency_id':
                           sale.pricelist_id.currency_id.id,
                           'payment_date': date,
                           'amount': self[0].amount_advance,
                           'sale_id': sale.id,
                           'name': _("Advance Payment") + " - " + sale.name,
                           'communication':
                           self[0].payment_ref or sale.name,
                           'payment_method_id': self.env.
                           ref('account.account_payment_method_manual_in').id
                           }
            payment = payment_obj.create(payment_res)
            payment.post()

        return {
            'type': 'ir.actions.act_window_close',
        }
