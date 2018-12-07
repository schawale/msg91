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
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    sale_id = fields.Many2one('sale.order', "Sale", readonly=True,
                              states={'draft': [('readonly', False)]})

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
    outstanding_amount = fields.Float(string='Outstanding Amount')

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

    @api.onchange('partner_type','partner_id')
    def onchange_outstanding_amount(self):
        if self.partner_type=='customer':
            self.outstanding_amount = self.partner_id.credit
        elif  self.partner_type=='supplier':
            self.outstanding_amount = self.partner_id.debit
        else:
            self.outstanding_amount =0.0
            
    @api.onchange('journal_id', 'destination_journal_id')
    def onchange_journal(self):
        if self.journal_id:
            self.journal_name = self.journal_id.type
            self.payment_type_mode = ''
        if self.destination_journal_id:
            self.tra_journal_name = self.destination_journal_id.type

    @api.model
    def create(self, vals):
        print('vals---',vals)
        if vals['journal_name'] == 'bank':
            if not vals['payment_type_mode']:
                raise UserError(_("Please select Payment Mode."))
        res = super(AccountPayment, self).create(vals)
        return res

    @api.multi
    def amount_in_words(self, n):
        n = int(n)
        words = ''

        units = ['', 'One', 'Two', 'Three', 'Four', 'Five',
                 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven',
                 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen',
                 'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', 'Ten', 'Twenty', 'Thirty', 'Forty', 'Fifty',
                'Sixty', 'Seventy', 'Eighty', 'Ninety']

        for group in ['', 'hundred', 'thousand', 'lakh', 'crore']:

            if group in ['', 'thousand', 'lakh']:
                n, digits = n // 100, n % 100
            elif group == 'hundred':
                n, digits = n // 10, n % 10
            else:
                digits = n

            if digits in range(1, 20):
                words = units[digits] + ' ' + group + ' ' + words
            elif digits in range(20, 100):
                ten_digit, unit_digit = digits // 10, digits % 10
                words = tens[ten_digit] + ' ' + units[unit_digit] + ' ' + group + ' ' + words
            elif digits >= 100:
                words = self.amount_in_words(digits) + ' crore ' + words
        words = words + ' Only'
        return words.title()


class BankChequeDetail(models.Model):
    _name = 'bank.payment.cheque'
    _description = "Bank Detail"

    name = fields.Char(string="Bank Name")
