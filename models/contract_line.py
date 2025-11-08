# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ContractLine(models.Model):
    _name = "contract.line"
    _description = "Contract Line"
    _order = "contract_id, sequence, id"

    sequence = fields.Integer(string="Sequence", default=10)
    
    contract_id = fields.Many2one(
        'contract.contract',
        string="Hợp đồng",
        required=True,
        ondelete='cascade'
    )
    
    product_id = fields.Many2one(
        'product.product',
        string="Sản phẩm",
        required=True
    )
    
    name = fields.Text(
        string="Mô tả",
        required=True
    )
    
    # Manufacturer and origin
    manufacturer_id = fields.Many2one(
        'res.partner',
        string="Hãng SX",
        domain=[('is_company', '=', True)]
    )
    origin_country_id = fields.Many2one(
        'res.country',
        string="Nước SX"
    )
    
    product_code = fields.Char(
        string="Mã hàng",
        related='product_id.default_code',
        readonly=True
    )
    
    hs_code = fields.Char(string="Mã HS hàng hóa")
    
    uom_id = fields.Many2one(
        'uom.uom',
        string="Đơn vị tính",
        required=True
    )
    
    quantity = fields.Float(
        string="Số lượng",
        required=True,
        default=1.0,
        digits='Product Unit of Measure'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string="Tiền tệ",
        related='contract_id.currency_id',
        readonly=True
    )
    
    price_unit = fields.Monetary(
        string="Đơn giá",
        required=True,
        currency_field='currency_id'
    )
    
    price_subtotal = fields.Monetary(
        string="Thành tiền",
        compute='_compute_price_subtotal',
        store=True,
        currency_field='currency_id'
    )
    
    # Link to sale order line
    sale_order_line_id = fields.Many2one(
        'sale.order.line',
        string="Dòng SO nguồn",
        ondelete='set null'
    )
    
    sale_order_id = fields.Many2one(
        'sale.order',
        string="SO nguồn",
        related='sale_order_line_id.order_id',
        readonly=True,
        store=True
    )

    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.display_name
            self.uom_id = self.product_id.uom_id
            self.price_unit = self.product_id.list_price

