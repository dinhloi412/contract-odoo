# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ContractAppendixLine(models.Model):
    _name = "contract.appendix.line"
    _description = "Contract Appendix Line"
    _order = "appendix_id, sequence, id"

    sequence = fields.Integer(string="Sequence", default=10)
    
    appendix_id = fields.Many2one(
        'contract.appendix',
        string="Phụ lục",
        required=True,
        ondelete='cascade'
    )
    
    product_id = fields.Many2one(
        'product.product',
        string="Sản phẩm/Dịch vụ"
    )
    
    description = fields.Text(
        string="Mô tả"
    )
    
    uom_id = fields.Many2one(
        'uom.uom',
        string="Đơn vị tính"
    )
    
    quantity = fields.Float(
        string="Số lượng",
        default=1.0,
        digits='Product Unit of Measure'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string="Tiền tệ",
        related='appendix_id.currency_id',
        readonly=True
    )
    
    price_unit = fields.Monetary(
        string="Đơn giá",
        currency_field='currency_id'
    )
    
    price_subtotal = fields.Monetary(
        string="Thành tiền",
        compute='_compute_price_subtotal',
        store=True,
        currency_field='currency_id'
    )
    
    change_action = fields.Selection(
        [
            ('add', 'Bổ sung'),
            ('adjust', 'Điều chỉnh'),
            ('remove', 'Giảm bớt/Gỡ'),
        ],
        string="Loại thay đổi",
        default='add'
    )
    
    # References
    ref_contract_line_id = fields.Many2one(
        'contract.line',
        string="Dòng HĐ tham chiếu",
        ondelete='set null'
    )
    
    sale_order_line_id = fields.Many2one(
        'sale.order.line',
        string="Dòng SO tham chiếu",
        ondelete='set null'
    )

    @api.depends('quantity', 'price_unit', 'change_action')
    def _compute_price_subtotal(self):
        for line in self:
            subtotal = line.quantity * line.price_unit
            # If removing, make it negative
            if line.change_action == 'remove':
                subtotal = -abs(subtotal)
            line.price_subtotal = subtotal

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.display_name
            self.uom_id = self.product_id.uom_id
            self.price_unit = self.product_id.list_price

    @api.onchange('ref_contract_line_id')
    def _onchange_ref_contract_line_id(self):
        """Auto-fill from referenced contract line"""
        if self.ref_contract_line_id:
            self.product_id = self.ref_contract_line_id.product_id
            self.description = self.ref_contract_line_id.name
            self.uom_id = self.ref_contract_line_id.uom_id
            self.quantity = self.ref_contract_line_id.quantity
            self.price_unit = self.ref_contract_line_id.price_unit

