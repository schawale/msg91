# -*- encoding: UTF-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2015-Today Laxicon Solution.
#    (<http://laxicon.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from odoo import models, fields, api, _


class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"

    payment_type_mode = fields.Selection([('cheque', 'Cheque'), ('draft', 'Draft'), ('rtgs', 'RTGS'), ('neft', 'NEFT'), ('cash', 'Cash')], string='Payment mode', readonly=True,
                                         track_visibility='onchange', states={'draft': [('readonly', False)]})
    is_account_pay = fields.Boolean(string="A/C pay ?", default=False, track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    cheque_payee_name = fields.Char(string='Cheque Payer Name', track_visibility='onchange')
    cheque_date = fields.Date(string='Cheque Date', track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    dd_date = fields.Date(string='D.D. Date', track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    transaction_date = fields.Date(string='Transaction Date', track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    cheque_number = fields.Char(string='Cheque Number', track_visibility='onchange')
    journal_name = fields.Char(string='journal name')
    bank_id = fields.Many2one('res.bank', string="Company Bank Name", track_visibility='onchange')
    acc_no = fields.Many2one('res.partner.bank', string="Company Account No", track_visibility='onchange')
    transaction_number = fields.Char(string="Transaction ID", track_visibility='onchange')
    dd_number = fields.Char(string="D.D. Number", track_visibility='onchange')
    cust_bank_name = fields.Many2one('bank.payment.cheque', string="Customer Bank Name", track_visibility='onchange')
    cash_payee_name = fields.Char(string="Payer Name", track_visibility="onchange")
    tra_bank_id = fields.Many2one('res.bank', string="Company Bank Name", track_visibility='onchange')
    tra_acc_no = fields.Many2one('res.partner.bank', string="Company Account No", track_visibility='onchange')
    tra_journal_name = fields.Char(string='journal name')

    @api.onchange('bank_id', 'tra_bank_id')
    def onchange_bank_id(self):
        bank_id = self.bank_id
        if self.payment_type == 'transfer':
            bank_id = self.tra_bank_id
        if bank_id:
            acc_list = []
            acc_ids = self.env['res.partner.bank'].search([('bank_id', '=', bank_id.id)])
            for acc in acc_ids:
                acc_list.append(acc.id)
            if self.payment_type == 'transfer':
                return {'domain': {'tra_acc_no': [('id', 'in', acc_list)]}}
            else:
                return {'domain': {'acc_no': [('id', 'in', acc_list)]}}

    @api.onchange('journal_id', 'destination_journal_id')
    def onchange_journal(self):
        if self.journal_id:
            self.journal_name = self.journal_id.type
            self.payment_type_mode = ''
        if self.destination_journal_id:
            self.tra_journal_name = self.destination_journal_id.type

    def get_payment_vals(self):
        res = super(AccountRegisterPayments, self).get_payment_vals()
        res.update({
                'payment_type_mode': self.payment_type_mode,
                'is_account_pay': self.is_account_pay,
                'cheque_date': self.cheque_date,
                'dd_date': self.dd_date,
                'transaction_date': self.transaction_date,
                'cheque_number': self.cheque_number,
                'journal_name': self.journal_name,
                'bank_id': self.bank_id.id,
                'acc_no': self.acc_no.id,
                'transaction_number': self.transaction_number,
                'dd_number': self.dd_number,
                'cust_bank_name': self.cust_bank_name,
                'cash_payee_name': self.cash_payee_name,
                'tra_bank_id': self.tra_bank_id,
                'tra_acc_no': self.tra_acc_no,
                'tra_journal_name': self.tra_journal_name
            })
        return res
