from odoo import api, fields, models,_
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from datetime import datetime
from collections import defaultdict
import math
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare
from odoo.tools import float_round

class MRPProduction(models.Model):
    _inherit = "mrp.production"
    
    @api.one
    @api.depends('state')
    def _compute_color(self):
        print ("compute coolr getting called------------------")
        if self.state=='progress':
#            red6,blu4,darkbrown5,white0,red dark1,orange2,yellow3,7darksky blue,8darkest leafy green,9actualred
            self.member_color=3
        elif self.state=='done':
            self.member_color=4
        elif self.state=='cancel':
            self.member_color=6
        else:
            self.member_color=0
            
    res_user_ids = fields.Many2many('res.users','mrp_workorder_resusers_rel', 'mrp_workorder_id', 'user_id')
    member_color = fields.Integer(string='Color', store=True, readonly=True, compute='_compute_color',
                                      track_visibility='always')
    
    def _workorders_create(self, bom, bom_data):
        """
        :param bom: in case of recursive boms: we could create work orders for child
                    BoMs
        """
        workorders = self.env['mrp.workorder']
        bom_qty = bom_data['qty']
        # Initial qty producing
        if self.product_id.tracking == 'serial':
            quantity = 1.0
        else:
            quantity = self.product_qty - sum(self.move_finished_ids.mapped('quantity_done'))
            quantity = quantity if (quantity > 0) else 0

        for operation in bom.routing_id.operation_ids:
            # create workorder
            cycle_number = math.ceil(bom_qty / operation.workcenter_id.capacity)  # TODO: float_round UP
            duration_expected = (operation.workcenter_id.time_start +
                                 operation.workcenter_id.time_stop +
                                 cycle_number * operation.time_cycle * 100.0 / operation.workcenter_id.time_efficiency)
            workorder = workorders.create({
                'name': operation.name,
                'production_id': self.id,
                'workcenter_id': operation.workcenter_id.id,
                'operation_id': operation.id,
                'duration_expected': duration_expected,
                'res_user_ids': [(6, 0, self.res_user_ids.ids)],
                'state': len(workorders) == 0 and 'ready' or 'pending',
                'qty_producing': quantity,
                'capacity': operation.workcenter_id.capacity,
            })
            if workorders:
                workorders[-1].next_work_order_id = workorder.id
            workorders += workorder

            # assign moves; last operation receive all unassigned moves (which case ?)
            moves_raw = self.move_raw_ids.filtered(lambda move: move.operation_id == operation)
            if len(workorders) == len(bom.routing_id.operation_ids):
                moves_raw |= self.move_raw_ids.filtered(lambda move: not move.operation_id)
            moves_finished = self.move_finished_ids.filtered(lambda move: move.operation_id == operation) #TODO: code does nothing, unless maybe by_products?
            moves_raw.mapped('move_line_ids').write({'workorder_id': workorder.id})
            (moves_finished + moves_raw).write({'workorder_id': workorder.id})

            workorder._generate_lot_ids()
        return workorders

class MRPWorkOrder(models.Model):
    _inherit = "mrp.workorder"
    
    @api.one
    @api.depends('state')
    def _compute_color(self):
        print ("compute coolr getting called------------------")
        if self.state=='progress':
#            red6,blu4,darkbrown5,white0,red dark1,orange2,yellow3,7darksky blue,8darkest leafy green,9actualred
            self.member_color=3
        elif self.state=='done':
            self.member_color=4
        elif self.state=='cancel':
            self.member_color=6
        elif self.state=='pending':
            self.member_color=5
        elif self.state=='ready':
            self.member_color=7
        else:
            self.member_color=0
    
    res_user_ids = fields.Many2many('res.users','mrp_workorder_resusers_rel', 'mrp_workorder_id', 'user_id')
    member_color = fields.Integer(string='Color', store=True, readonly=True, compute='_compute_color',
                                      track_visibility='always')

    @api.multi
    def record_production(self):
        login_user_id=self.env.uid
        user_id = self.env['res.users'].browse(login_user_id)
        manager = user_id.has_group('mrp.group_mrp_manager')
        for res_user_id in self.res_user_ids:
            if res_user_id.id==login_user_id or manager==True:
                self.ensure_one()
                if self.qty_producing <= 0:
                    raise UserError(_('Please set the quantity you are currently producing. It should be different from zero.'))

                if (self.production_id.product_id.tracking != 'none') and not self.final_lot_id and self.move_raw_ids:
                    raise UserError(_('You should provide a lot/serial number for the final product'))

                # Update quantities done on each raw material line
                # For each untracked component without any 'temporary' move lines,
                # (the new workorder tablet view allows registering consumed quantities for untracked components)
                # we assume that only the theoretical quantity was used
                for move in self.move_raw_ids:
                    if move.has_tracking == 'none' and (move.state not in ('done', 'cancel')) and move.bom_line_id\
                                and move.unit_factor and not move.move_line_ids.filtered(lambda ml: not ml.done_wo):
                        rounding = move.product_uom.rounding
                        if self.product_id.tracking != 'none':
                            qty_to_add = float_round(self.qty_producing * move.unit_factor, precision_rounding=rounding)
                            move._generate_consumed_move_line(qty_to_add, self.final_lot_id)
                        else:
                            move.quantity_done += float_round(self.qty_producing * move.unit_factor, precision_rounding=rounding)

                # Transfer quantities from temporary to final move lots or make them final
                for move_line in self.active_move_line_ids:
                    # Check if move_line already exists
                    if move_line.qty_done <= 0:  # rounding...
                        move_line.sudo().unlink()
                        continue
                    if move_line.product_id.tracking != 'none' and not move_line.lot_id:
                        raise UserError(_('You should provide a lot/serial number for a component'))
                    # Search other move_line where it could be added:
                    lots = self.move_line_ids.filtered(lambda x: (x.lot_id.id == move_line.lot_id.id) and (not x.lot_produced_id) and (not x.done_move) and (x.product_id == move_line.product_id))
                    if lots:
                        lots[0].qty_done += move_line.qty_done
                        lots[0].lot_produced_id = self.final_lot_id.id
                        move_line.sudo().unlink()
                    else:
                        move_line.lot_produced_id = self.final_lot_id.id
                        move_line.done_wo = True

                # One a piece is produced, you can launch the next work order
                if self.next_work_order_id.state == 'pending':
                    self.next_work_order_id.state = 'ready'

                self.move_line_ids.filtered(
                    lambda move_line: not move_line.done_move and not move_line.lot_produced_id and move_line.qty_done > 0
                ).write({
                    'lot_produced_id': self.final_lot_id.id,
                    'lot_produced_qty': self.qty_producing
                })

                # If last work order, then post lots used
                # TODO: should be same as checking if for every workorder something has been done?
                if not self.next_work_order_id:
                    production_move = self.production_id.move_finished_ids.filtered(
                                        lambda x: (x.product_id.id == self.production_id.product_id.id) and (x.state not in ('done', 'cancel')))
                    if production_move.product_id.tracking != 'none':
                        move_line = production_move.move_line_ids.filtered(lambda x: x.lot_id.id == self.final_lot_id.id)
                        if move_line:
                            move_line.product_uom_qty += self.qty_producing
                        else:
                            move_line.create({'move_id': production_move.id,
                                     'product_id': production_move.product_id.id,
                                     'lot_id': self.final_lot_id.id,
                                     'product_uom_qty': self.qty_producing,
                                     'product_uom_id': production_move.product_uom.id,
                                     'qty_done': self.qty_producing,
                                     'workorder_id': self.id,
                                     'location_id': production_move.location_id.id,
                                     'location_dest_id': production_move.location_dest_id.id,
                            })
                    else:
                        production_move.quantity_done += self.qty_producing

                if not self.next_work_order_id:
                    for by_product_move in self.production_id.move_finished_ids.filtered(lambda x: (x.product_id.id != self.production_id.product_id.id) and (x.state not in ('done', 'cancel'))):
                        if by_product_move.has_tracking == 'none':
                            by_product_move.quantity_done += self.qty_producing * by_product_move.unit_factor

                # Update workorder quantity produced
                self.qty_produced += self.qty_producing

                if self.final_lot_id:
                    self.final_lot_id.use_next_on_work_order_id = self.next_work_order_id
                    self.final_lot_id = False

                # Set a qty producing
                rounding = self.production_id.product_uom_id.rounding
                if float_compare(self.qty_produced, self.production_id.product_qty, precision_rounding=rounding) >= 0:
                    self.qty_producing = 0
                elif self.production_id.product_id.tracking == 'serial':
                    self._assign_default_final_lot_id()
                    self.qty_producing = 1.0
                    self._generate_lot_ids()
                else:
                    self.qty_producing = float_round(self.production_id.product_qty - self.qty_produced, precision_rounding=rounding)
                    self._generate_lot_ids()

                if self.next_work_order_id and self.production_id.product_id.tracking != 'none':
                    self.next_work_order_id._assign_default_final_lot_id()

                if float_compare(self.qty_produced, self.production_id.product_qty, precision_rounding=rounding) >= 0:
                    self.button_finish()
            else:
                raise UserError(_("You are not assign for this workorder contact administrator."))
              
        return True
    
    
    @api.multi
    def button_start(self):
        login_user_id=self.env.uid
        user_id = self.env['res.users'].browse(login_user_id)
        manager = user_id.has_group('mrp.group_mrp_manager')
        # TDE CLEANME
        timeline = self.env['mrp.workcenter.productivity']
        for res_user_id in self.res_user_ids:
            if res_user_id.id==login_user_id or manager==True:
                if self.duration < self.duration_expected:
                    loss_id = self.env['mrp.workcenter.productivity.loss'].search([('loss_type','=','productive')], limit=1)
                    if not len(loss_id):
                        raise UserError(_("You need to define at least one productivity loss in the category 'Productivity'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
                else:
                    loss_id = self.env['mrp.workcenter.productivity.loss'].search([('loss_type','=','performance')], limit=1)
                    if not len(loss_id):
                        raise UserError(_("You need to define at least one productivity loss in the category 'Performance'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
                for workorder in self:
                    if workorder.production_id.state != 'progress':
                        workorder.production_id.write({
                            'state': 'progress',
                            'date_start': datetime.now(),
                        })
                    timeline.create({
                        'workorder_id': workorder.id,
                        'workcenter_id': workorder.workcenter_id.id,
                        'description': _('Time Tracking: ')+self.env.user.name,
                        'loss_id': loss_id[0].id,
                        'date_start': datetime.now(),
                        'user_id': self.env.user.id
                    })
                return self.write({'state': 'progress',
                            'date_start': datetime.now(),
                })
            else:
                raise UserError(_("You are not assign for this workorder contact administrator."))
                        
    @api.multi
    def button_scrap(self):
        login_user_id=self.env.uid
        user_id = self.env['res.users'].browse(login_user_id)
        manager = user_id.has_group('mrp.group_mrp_manager')
        for res_user_id in self.res_user_ids:
            if res_user_id.id==login_user_id or manager==True:
                self.ensure_one()
                return {
                    'name': _('Scrap'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.scrap',
                    'view_id': self.env.ref('stock.stock_scrap_form_view2').id,
                    'type': 'ir.actions.act_window',
                    'context': {'default_workorder_id': self.id, 'default_production_id': self.production_id.id, 'product_ids': (self.production_id.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel')) | self.production_id.move_finished_ids.filtered(lambda x: x.state == 'done')).mapped('product_id').ids},
                    # 'context': {'product_ids': self.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel')).mapped('product_id').ids + [self.production_id.product_id.id]},
                    'target': 'new',
                }
            else:
                raise UserError(_("You are not assign for this workorder contact administrator."))
    @api.multi
    def button_pending(self):
        login_user_id=self.env.uid
        user_id = self.env['res.users'].browse(login_user_id)
        manager = user_id.has_group('mrp.group_mrp_manager') 
        for res_user_id in self.res_user_ids:
            if res_user_id.id==login_user_id or manager==True:
                self.end_previous()
            else:
                raise UserError(_("You are not assign for this workorder contact administrator."))
              
        return True
